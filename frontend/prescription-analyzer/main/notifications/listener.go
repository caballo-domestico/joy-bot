package notifications

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
	msg.Key = jsonMap["key"]
	msg.Username = jsonMap["username"]
	msg.S3link = jsonMap["s3link"]
	msg.Bucket = jsonMap["bucket"]
	return err
}

func Listen(out chan *PrescriptionUploadedMsg, topic Topic, kafkaAddr string) {

	// continously listen for new prescription uploads
	r := kafka.NewReader(kafka.ReaderConfig{
		Brokers:   []string{kafkaAddr},
		Topic:     string(topic),
		Partition: 0,
		MinBytes:  10e3, // 10KB
		MaxBytes:  10e6, // 10MB
	})
	defer r.Close()
	r.SetOffset(-1)
	log.Info("started listener for new prescription uploads")
	for {
		m, err := r.ReadMessage(context.Background())
		if err != nil {
			log.Error(err)
		} else {
			log.Debug("Received message in topic ", string(m.Topic), "\n")

			switch topic {
			case PRESCRIPTION_UPLOADED:
				// parses prescription uploaded notification
				msg := new(PrescriptionUploadedMsg)
				err := msg.fromJSON(m.Value)
				if err != nil {
					log.Error(err)
					continue
				}
				out <- msg
			}
		}
	}
}
