package main

import (
	"fmt"
	"testing"

	log "github.com/sirupsen/logrus"
)

func TestLoadPrescribedDrugsByPatient(t *testing.T) {

	log.SetLevel(log.DebugLevel)
	patientName := "test"

	drugs, err := loadPrescribedDrugsByPatient(patientName)
	if err != nil {
		log.Error(err)
		t.FailNow()
	}

	for _, drug := range drugs {
		log.Debug(fmt.Sprintf("%s --> %s", drug.Name, drug.Frequency))
	}
}
