package main

import (
	"context"
	"encoding/json"
	"fmt"

	log "github.com/sirupsen/logrus"

	//"github.com/aws/aws-sdk-go-v2/config"
	//"github.com/aws/aws-sdk-go-v2/service/s3"
	//"github.com/aws/aws-sdk-go-v2/service/textract"
	"github.com/segmentio/kafka-go"
)

type PrescriptionUploadedMsg struct {
	PrescriptionFilename string
	Username             string
}

func (msg *PrescriptionUploadedMsg) fromJSON(data []byte) error {

	jsonMap := make(map[string]string)
	err := json.Unmarshal(data, &jsonMap)
	if err != nil {
		log.Error(err)
		return fmt.Errorf("unable to parse json")
	}
	log.Debug(string(fmt.Sprint(jsonMap)))
	msg.PrescriptionFilename = jsonMap["filename"]
	msg.Username = jsonMap["username"]
	return err
}

func main() {

	log.SetLevel(log.DebugLevel)
	log.SetReportCaller(true)

	// TODO: continously listen for new prescription uploads
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
			log.Debug("Received message in topic ", string(m.Topic))

			// parse json message to extract prescription file name and user name
			msg := new(PrescriptionUploadedMsg)
			msg.fromJSON(m.Value)

			/*
				// TODO: fetch prescription file from S3
				cfg, err := config.LoadDefaultConfig(context.TODO())
				if err != nil {
					log.Error(err)
				}

				s3Client := s3.NewFromConfig(cfg)

				// TODO: Analyze prescription content with AWS Textract
				textractClient := textract.NewFromConfig(cfg)
			*/
			// TODO: store prescription data in DynamoDB

		}
	}

}
