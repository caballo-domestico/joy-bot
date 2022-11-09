package notifications

import (
	"context"
	"google.golang.org/protobuf/proto"
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

func (msg *PrescriptionUploadedMsg) fromSerialized(data []byte) error {

	deserialized := new(PrescriptionUploaded)
	err := proto.Unmarshal(data, deserialized)
	if err != nil {
		log.Error(err)
		return fmt.Errorf("failed to deserialize message")
	}
	msg.Bucket = deserialized.Bucket
	msg.Key = deserialized.Key
	msg.S3link = deserialized.S3Link
	msg.Username = deserialized.Username

	return nil
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
				err := msg.fromSerialized(m.Value)
				if err != nil {
					log.Error(err)
					continue
				}
				out <- msg
			}
		}
	}
}
