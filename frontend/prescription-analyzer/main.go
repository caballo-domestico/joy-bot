package main

import (
	"context"
	"encoding/json"
	"fmt"

	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/textract"
	textractTypes "github.com/aws/aws-sdk-go-v2/service/textract/types"
	log "github.com/sirupsen/logrus"

	"github.com/segmentio/kafka-go"
)

type PrescriptionUploadedMsg struct {
	Key      string // key used to retrieve the prescription from S3
	Username string // username of the user who uploaded the prescription
	S3link   string // http link to the prescription in S3 (private)
	Bucket   string // S3 bucket name where the prescription is stored
}

func (msg *PrescriptionUploadedMsg) fromJSON(data []byte) error {

	jsonMap := make(map[string]string)
	err := json.Unmarshal(data, &jsonMap)
	if err != nil {
		log.Error(err)
		return fmt.Errorf("unable to parse json")
	}
	log.Debug(fmt.Sprint(jsonMap))
	msg.Key = jsonMap["key"]
	msg.Username = jsonMap["username"]
	msg.S3link = jsonMap["s3link"]
	msg.Bucket = jsonMap["bucket"]
	return err
}

func main() {

	log.SetLevel(log.DebugLevel)
	log.SetReportCaller(true)

	// continously listen for new prescription uploads
	r := kafka.NewReader(kafka.ReaderConfig{
		Brokers:   []string{"kafka:9092"},
		Topic:     "prescription_uploaded",
		Partition: 0,
		MinBytes:  10e3, // 10KB
		MaxBytes:  10e6, // 10MB
	})
	defer r.Close()
	r.SetOffset(-1)

	for {
		m, err := r.ReadMessage(context.Background())
		if err != nil {
			log.Error(err)
		} else {
			log.Debug("Received message in topic ", string(m.Topic), "\n")

			// parses prescription uploaded notification
			msg := new(PrescriptionUploadedMsg)
			msg.fromJSON(m.Value)

			log.Debug("Parsed message")
			// Loads aws configs and credentials from default files in ~/.aws .
			// These configs are needed from aws clients
			cfg, err := config.LoadDefaultConfig(context.TODO())
			if err != nil {
				log.Error(err)
				continue
			}
			log.Debug("Loaded aws config")

			// TODO: Analyze prescription content with AWS Textract
			textractIn := &textract.AnalyzeDocumentInput{
				Document: &textractTypes.Document{
					S3Object: &textractTypes.S3Object{
						Bucket: &msg.Bucket,
						Name:   &msg.Key,
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
				continue
			}
			log.Debug("Received textract response")

			for _, block := range textractOut.Blocks {

				log.Debug("Block type: ", block.BlockType)
				// TODO: https://docs.aws.amazon.com/textract/latest/dg/examples-extract-kvp.html

			}
			log.Debug("Analyzed prescription")
			// TODO: Recognize which medications has been prescribed and how often.

			// TODO: store prescription data in DynamoDB
		}
	}

}
