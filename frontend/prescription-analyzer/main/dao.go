package main

import (
	"context"
	"fmt"
	"strings"

	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb/types"
	log "github.com/sirupsen/logrus"
)

type DynamoDBTableName string

const (
	PRESCRIPTION_ANALYSIS DynamoDBTableName = "Prescription_analysis"
)

const (
	KEY_PREFIX_DRUG      = "DRUG"
	KEY_PREFIX_FREQUENCY = "FREQUENCY"
	KEY_PREFIX_DRUGS     = "DRUGS"
)

func newDynamoDBClient() (*dynamodb.Client, error) {
	cfg, err := config.LoadDefaultConfig(context.TODO())
	if err != nil {
		log.Error(err)
		return nil, fmt.Errorf("couldn't load default config")
	}
	return dynamodb.NewFromConfig(cfg), nil
}

func storeAnalysis(relationships map[string]string, prescriptionId string) error {

	client, err := newDynamoDBClient()
	if err != nil {
		log.Error(err)
		return fmt.Errorf("couldn't create dynamodb client")
	}

	// crafts a dynamodb item from the relationships map
	item := map[string]types.AttributeValue{}
	item[KEY_PREFIX_DRUGS] = &types.AttributeValueMemberL{Value: []types.AttributeValue{}}
	drugList := &(item[KEY_PREFIX_DRUGS].(*types.AttributeValueMemberL).Value)
	for key, value := range relationships {
		// couple each prescribed drug with its frequency and aggregate the couples in a
		// list. All other keys are stored with their respective values as is.
		// It is assumed that the drug name key is DRUGi and the frequency key
		// is FREQUENCYi, where i is the index of the drug in the prescription
		if strings.Contains(key, KEY_PREFIX_DRUG) {
			*drugList = append(*drugList, &types.AttributeValueMemberM{
				Value: map[string]types.AttributeValue{
					KEY_PREFIX_DRUG:      &types.AttributeValueMemberS{Value: value},
					KEY_PREFIX_FREQUENCY: &types.AttributeValueMemberS{Value: relationships[KEY_PREFIX_FREQUENCY+key[len(key)-3:]]},
				},
			})
		} else if !strings.Contains(key, KEY_PREFIX_FREQUENCY) {
			item[key] = &types.AttributeValueMemberS{Value: value}
		}
	}
	// add primary key to key-value pairs
	item["id"] = &types.AttributeValueMemberS{Value: prescriptionId}

	// crafts a dynamodb put item request
	tablename := string(PRESCRIPTION_ANALYSIS)
	dynamoDBRequest := &dynamodb.PutItemInput{
		Item:      item,
		TableName: &tablename,
	}

	// sends the request
	_, err = client.PutItem(context.TODO(), dynamoDBRequest)
	if err != nil {
		log.Error(err)
		return fmt.Errorf("error encountered after requesting put item to dynamodb ")
	}

	return nil
}
