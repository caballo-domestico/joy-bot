package main

import (
	"flag"
	"fmt"

	"joybot/panalyzer/main/analyzer"
	"joybot/panalyzer/main/config"
	"joybot/panalyzer/main/dao"
	"joybot/panalyzer/main/notifications"
	"joybot/panalyzer/main/rpc"

	log "github.com/sirupsen/logrus"

	"github.com/sony/gobreaker"
)

func main() {

	log.SetLevel(log.DebugLevel)
	log.SetReportCaller(true)

	config.KafkaAddr = *flag.String("kafka-addr", "kafka:9092", "kafka_address:port")
	config.RpcAddr = *flag.String("rpc-addr", "50051", "rpc_address:port")
	config.RpcNetwork = *flag.String("rpc-network", "tcp", "same network values as go net.Listen")
	config.CbTimeout = *flag.Duration("cb-timeout", 30, "duration of open circuit state")
	config.CbMaxRequest = uint32(*flag.Uint("cb-max-requests", 0, "max number of requests before circuit breaker opens"))

	flag.Parse()

	// create a circuit breaker to use globally
	cb := gobreaker.NewCircuitBreaker(gobreaker.Settings{
		Name:        "main",
		MaxRequests: config.CbMaxRequest,
		Timeout:     config.CbTimeout,
	})

	// we spawn a goroutine which notify main thread whenever a message has
	// been posted on topic
	msgs := make(chan *notifications.PrescriptionUploadedMsg)
	go notifications.Listen(msgs, notifications.PRESCRIPTION_UPLOADED)

	// goroutine which handles incoming rpc requests
	go rpc.Listen(config.RpcNetwork, config.RpcAddr)

	for {
		msg := <-msgs

		// Make Textract analyze the prescription to get key-value pairs
		pairs, err := cb.Execute(func() (interface{}, error) {
			pairs, err := analyzer.AnalyzeS3Object(msg.Bucket, msg.Key)
			if err != nil {
				log.Error(err)
				return nil, err
			}
			return pairs, err
		})
		if err != nil {
			log.Error(err)
			continue
		}

		log.Info("prescription analyzed")
		log.Debug(fmt.Sprint(pairs))

		// store prescription data in DynamoDB
		_, err = cb.Execute(func() (interface{}, error) {
			err := dao.StoreAnalysis(pairs.(map[string]string), msg.Key)
			if err != nil {
				log.Error(err)
			}
			return nil, err
		})
		if err != nil {
			log.Error(err)
			continue
		}
		log.Info("prescription analysis stored")
	}

}
