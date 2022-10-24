package main

import (
	"context"

	log "github.com/sirupsen/logrus"

	"github.com/segmentio/kafka-go"
)

func main() {

	// TODO: continously listen for new prescription uploads
	r := kafka.NewReader(kafka.ReaderConfig{
		Brokers:   []string{"kafka:9092"},
		Topic:     "prescription_uploaded",
		Partition: 0,
		MinBytes:  10e3, // 10KB
		MaxBytes:  10e6, // 10MB
	})
	r.SetOffset(-1)

	for {
		m, err := r.ReadMessage(context.Background())
		if err != nil {
			log.Error(err)
		} else {
			log.Info("Message: ", string(m.Value))
		}
	}
	if err := r.Close(); err != nil {
		log.Fatal("failed to close reader:", err)
	} 
	
	// TODO: Analyze prescription content with AWS Textract

	// TODO: store prescription data in DynamoDB
}
