package main

import (
	"fmt"

	log "github.com/sirupsen/logrus"
)

func main() {

	log.SetLevel(log.InfoLevel)
	log.SetReportCaller(true)

	// we spawn a goroutine which notify main thread whenever a message has
	// been posted on topic
	msgs := make(chan *PrescriptionUploadedMsg)
	go listen(msgs)
	for {
		msg := <-msgs

		// Make Textract analyze the prescription to get key-value pairs
		pairs, err := analyzeS3Object(msg.Bucket, msg.Key)
		if err != nil {
			log.Error(err)
			continue
		}

		log.Debug(fmt.Sprint(pairs))

		// store prescription data in DynamoDB
		storeAnalysis(pairs, msg.Key)
		log.Debug("prescription analysis ", msg.Key, " stored")
	}

}
