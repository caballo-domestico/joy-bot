package main

import (
	"context"
	"fmt"

	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb/types"
	log "github.com/sirupsen/logrus"
)

type DynamoDBTableName string

const (
	PRESCRIPTION_ANALYSIS DynamoDBTableName = "Prescription_analysis"
)

func storeAnalysis(relationships map[string]string, prescriptionId string) error {

	// creates dynamodb client
	cfg, err := config.LoadDefaultConfig(context.TODO())
	if err != nil {
		log.Error(err)
		return fmt.Errorf("couldn't load default config")
	}
	client := dynamodb.NewFromConfig(cfg)

	// crafts a dynamodb item from the relationships map
	item := map[string]types.AttributeValue{}
	for key, value := range relationships {
		item[key] = &types.AttributeValueMemberS{Value: value}
	}
	// add primary key to key-value pairs
	item["id"] = &types.AttributeValueMemberS{Value: prescriptionId}

	// crafts a dynamodb put item request
	tablename := string(PRESCRIPTION_ANALYSIS)
	dynamoDBRequest := &dynamodb.PutItemInput{
		Item:      item,
		TableName: &tablename,
	}

	// sends the request
	_, err = client.PutItem(context.TODO(), dynamoDBRequest)
	if err != nil {
		log.Error(err)
		return fmt.Errorf("error encountered after requesting put item to dynamodb ")
	}

	return nil
}
