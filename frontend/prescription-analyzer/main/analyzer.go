package main

import (
	"context"
	"fmt"

	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/textract"
	textractTypes "github.com/aws/aws-sdk-go-v2/service/textract/types"
	log "github.com/sirupsen/logrus"
)

type TextractBlocks []textractTypes.Block            // blocks returned by Textract in an AnalyzeDocument response
type TextractBlockMap map[string]textractTypes.Block // map with values as texract blocks and keys as block ids
type TextractEntityTypes []textractTypes.EntityType  // entity types in an AnalyzeDocument response

/*
	Returns true if an Amazon Textract entity type is present among given entity types
*/
func (entityTypes TextractEntityTypes) contains(entityType textractTypes.EntityType) bool {
	for _, e := range entityTypes {
		if e == entityType {
			return true
		}
	}
	return false
}

/*
	Returns the VALUE block associated with a KEY block.
	If no VALUE block is found, an empty block and a non-nil error are returned.
*/
func (valueMap TextractBlockMap) getBlockBykey(keyBlock textractTypes.Block) (textractTypes.Block, error) {
	for _, relationship := range keyBlock.Relationships {
		if relationship.Type == textractTypes.RelationshipTypeValue {
			for _, id := range relationship.Ids {
				return valueMap[id], nil
			}
		}
	}
	return textractTypes.Block{}, fmt.Errorf("no VALUE block found for key block %s", *keyBlock.Id)
}

/*
	Builds a string from texts of all CHILD blocks of a block, separated by
	spaces.
*/
func (blockMap TextractBlockMap) getTextFromBlock(block textractTypes.Block) string {
	var text string = ""

	for _, relationship := range block.Relationships {
		if relationship.Type == textractTypes.RelationshipTypeChild {
			for _, childId := range relationship.Ids {
				childBlock := blockMap[childId]
				if childBlock.BlockType == textractTypes.BlockTypeWord {
					text += *childBlock.Text + " "
				}
			}
		}
	}
	return text
}

/*
	Returns a map with the following semantycs:
	key: the text of a block with same id of a KEY block
	value: text of all VALUE blocks associated with the above mentioned KEY block
	See https://docs.aws.amazon.com/textract/latest/dg/examples-extract-kvp.html for more details.

*/
func (blocks TextractBlocks) getRelationships() (map[string]string, error) {

	relationshipsMap := make(map[string]string) // holds texts of VALUE blocks indexed by the text of their KEY block

	blockMap := make(map[string]textractTypes.Block) // Holds all blocks indexed by their id
	keyMap := make(map[string]textractTypes.Block)   // Holds all KEY blocks
	valueMap := make(map[string]textractTypes.Block) // Holds all VALUE blocks

	// Puts all blocks in blockMap and groups them among keyMap and valueMap
	for _, block := range blocks {
		id := *block.Id
		blockMap[id] = block
		if block.BlockType == textractTypes.BlockTypeKeyValueSet {
			if block.EntityTypes != nil && TextractEntityTypes(block.EntityTypes).contains(textractTypes.EntityTypeKey) {
				keyMap[id] = block
			} else {
				valueMap[id] = block
			}
		}
	}

	// For each KEY block, puts the text of all VALUE block associated with it
	// in the relationship map, using the text of the KEY block as key
	for id, keyBlock := range keyMap {
		valueBlock, err := TextractBlockMap(valueMap).getBlockBykey(keyBlock)
		if err != nil {
			log.Error(err)
			return nil, fmt.Errorf("unable to get value block for key block %s", id)
		}
		keyText := TextractBlockMap(blockMap).getTextFromBlock(keyBlock)
		valueText := TextractBlockMap(blockMap).getTextFromBlock(valueBlock)
		relationshipsMap[keyText] = valueText
	}

	return relationshipsMap, nil
}

func analyzeS3Object(bucketName string, objectName string) (map[string]string, error) {

	// Loads aws configs and credentials from default files in ~/.aws .
	// These configs are needed from aws clients
	cfg, err := config.LoadDefaultConfig(context.TODO())
	if err != nil {
		log.Error(err)
		return nil, fmt.Errorf("couldn't load default config")
	}
	log.Debug("Loaded aws config")

	// Analyze prescription content with AWS Textract
	textractIn := &textract.AnalyzeDocumentInput{
		Document: &textractTypes.Document{
			S3Object: &textractTypes.S3Object{
				Bucket: &bucketName,
				Name:   &objectName,
			},
		},
		FeatureTypes: []textractTypes.FeatureType{
			textractTypes.FeatureTypeForms,
		},
	}
	log.Debug("Prepared textract request")

	textractClient := textract.NewFromConfig(cfg)
	textractOut, err := textractClient.AnalyzeDocument(context.TODO(), textractIn)
	if err != nil {
		log.Error(err)
		return nil, fmt.Errorf("textract analysis response returned an error")
	}
	log.Debug("Received textract response")

	/*
		Textract response contains a list of blocks, each one of a given type.
		We are interested in the following types of blocks:
			- KEY_VALUE_SET (KEY and VALUE blocks)
			- WORD (CHILD blocks of KEY_VALUE_SET blocks)
		We need to process the response further to link the key and the values with the corresponding text.
		see https://docs.aws.amazon.com/textract/latest/dg/how-it-works-kvp.html for more details.
	*/
	relationships, err := TextractBlocks(textractOut.Blocks).getRelationships()
	if err != nil {
		log.Error(err)
		return nil, fmt.Errorf("couldn't extract relationships")
	}

	return relationships, nil

}
