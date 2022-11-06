package main

import (
	"flag"
	"fmt"

	"joybot/panalyzer/main/analyzer"
	"joybot/panalyzer/main/dao"
	"joybot/panalyzer/main/notifications"
	"joybot/panalyzer/main/rpc"

	log "github.com/sirupsen/logrus"
)

func main() {

	log.SetLevel(log.DebugLevel)
	log.SetReportCaller(true)

	kafkaAddr := flag.String("kafka-addr", "kafka:9092", "kafka_address:port")
	rpcAddr := flag.String("rpc-addr", "50051", "rpc_address:port")
	rpcNetwork := flag.String("rpc-network", "tcp", "same network values as go net.Listen")
	flag.Parse()

	// we spawn a goroutine which notify main thread whenever a message has
	// been posted on topic
	msgs := make(chan *notifications.PrescriptionUploadedMsg)
	go notifications.Listen(msgs, notifications.PRESCRIPTION_UPLOADED, *kafkaAddr)

	// goroutine which handles incoming rpc requests
	go rpc.Listen(*rpcNetwork, *rpcAddr)

	for {
		msg := <-msgs

		// Make Textract analyze the prescription to get key-value pairs
		pairs, err := analyzer.AnalyzeS3Object(msg.Bucket, msg.Key)
		if err != nil {
			log.Error(err)
			continue
		}
		log.Info("prescription analyzed")
		log.Debug(fmt.Sprint(pairs))

		// store prescription data in DynamoDB
		dao.StoreAnalysis(pairs, msg.Key)
		log.Info("prescription analysis stored")
	}

}
