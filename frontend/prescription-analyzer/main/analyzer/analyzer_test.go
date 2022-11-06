package analyzer

import (
	"fmt"
	"testing"

	log "github.com/sirupsen/logrus"
)

func TestAnalyzeS3Object(t *testing.T) {

	log.SetLevel(log.DebugLevel)
	bucketName := "joy-bot.prescriptions"
	prescritpionName := "test_Screenshot_20221016_200040.png"

	relationships, err := AnalyzeS3Object(bucketName, prescritpionName)
	if err != nil {
		t.Error(err)
	}
	log.Debug(fmt.Sprint(relationships))
}
