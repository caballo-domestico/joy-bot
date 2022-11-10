package rpc

import (
	"fmt"
	"joybot/panalyzer/main/config"
	"joybot/panalyzer/main/dao"
	"net"

	log "github.com/sirupsen/logrus"
	grpc "google.golang.org/grpc"

	"github.com/sony/gobreaker"
)

var cb = gobreaker.NewCircuitBreaker(gobreaker.Settings{
	Name:        "grpcServer",
	MaxRequests: config.CbMaxRequest,
	Timeout:     config.CbTimeout,
})

type prescriptionAnalyzerServer struct {
	UnimplementedPrescriptionAnalyzerServer // https://github.com/grpc/grpc-go/issues/3794#issuecomment-720599532
}

func (s prescriptionAnalyzerServer) GetPrescribedDrugs(in *PatientUsername, stream PrescriptionAnalyzer_GetPrescribedDrugsServer) error {

	log.Info("received rpc request for GetPrescribedDrugs")

	// Get the patient's prescribed drugs from the database
	prescribedDrugs, err := cb.Execute(func() (interface{}, error) {
		prescribedDrugs, err := dao.LoadPrescribedDrugs(in.GetUsername())
		if err != nil {
			log.Error(err)
			return nil, err
		}
		return prescribedDrugs, nil
	})
	if err != nil {
		log.Error(err)
		return fmt.Errorf("failed to get prescribed drugs from dynamodb")
	}
	// send serialized prescribed drugs to the client
	for _, prescribedDrug := range prescribedDrugs.([]dao.PrescribedDrug) {
		serializedPrescribedDrug := new(PrescribedDrug)
		serializedPrescribedDrug.Name = prescribedDrug.Name
		serializedPrescribedDrug.Frequency = prescribedDrug.Frequency
		if err := stream.Send(serializedPrescribedDrug); err != nil {
			log.Debug(err)
			return fmt.Errorf("error encountered while writing to client stream")
		}
	}
	return nil
}

func Listen(network string, addr string) {

	// creates gRPC server
	grpcServer := grpc.NewServer()
	RegisterPrescriptionAnalyzerServer(grpcServer, prescriptionAnalyzerServer{})
	defer grpcServer.GracefulStop()
	lis, err := net.Listen(network, addr)
	if err != nil {
		log.Debug(fmt.Errorf("failed to open socket with addr %s %s: %s", addr, network, err))
		return
	}

	// starts listening for incoming calls
	log.Info("started listener for rpc requests")
	for {
		if err := grpcServer.Serve(lis); err != nil {
			log.Debug(err)
		}
	}
}
