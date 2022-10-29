package main

import (
	"context"
	"encoding/json"
	"fmt"

	"github.com/segmentio/kafka-go"
	log "github.com/sirupsen/logrus"
)

// kafka topics
type Topic string

const (
	PRESCRIPTION_UPLOADED Topic = "prescription_uploaded"
)

// broker address
const KAFKA_ADDR string = "kafka:9092"

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

func listen(out chan *PrescriptionUploadedMsg) {
	// continously listen for new prescription uploads
	r := kafka.NewReader(kafka.ReaderConfig{
		Brokers:   []string{KAFKA_ADDR},
		Topic:     string(PRESCRIPTION_UPLOADED),
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
			err := msg.fromJSON(m.Value)
			if err != nil {
				log.Error(err)
				continue
			}
			log.Debug("Parsed message")
			out <- msg
		}
	}
}
