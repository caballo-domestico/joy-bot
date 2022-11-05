package dao

import (
	"context"
	"fmt"
	"strings"
	"time"

	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb/types"
	log "github.com/sirupsen/logrus"
)

type DynamoDBTableName string

const (
	PRESCRIPTION_ANALYSIS DynamoDBTableName = "Prescription_analysis"
)

type TableKey string

const (
	KEY_DRUG             TableKey = "DRUG"
	KEY_FREQUENCY        TableKey = "FREQUENCY"
	KEY_DRUGS            TableKey = "DRUGS"
	KEY_PATIENT          TableKey = "PATIENT"
	KEY_DATE             TableKey = "DATE"
	KEY_DATE_TIMESTAMPED TableKey = "DATE_TIMESTAMPED"
	KEY_ID               TableKey = "id"
)

const (
	DATE_FORMAT = "2006-1-2"
)

func (key TableKey) toExpressionAttributeValue() string {
	return fmt.Sprintf(":%s", string(key))
}
func (key TableKey) toExpressionAttributeName() string {
	return fmt.Sprintf("#%s", string(key))
}

func newDynamoDBClient() (*dynamodb.Client, error) {
	cfg, err := config.LoadDefaultConfig(context.TODO())
	if err != nil {
		log.Error(err)
		return nil, fmt.Errorf("couldn't load default config")
	}
	return dynamodb.NewFromConfig(cfg), nil
}

func toTimestamp(t time.Time) int64 {
	return t.Unix()
}

func StoreAnalysis(relationships map[string]string, prescriptionId string) error {

	client, err := newDynamoDBClient()
	if err != nil {
		log.Error(err)
		return fmt.Errorf("couldn't create dynamodb client")
	}

	// crafts a dynamodb item from the relationships map.
	// Attribute names are the keys of the map, attribute values are the values of the map,
	// both stripped of their leading and trailing whitespaces.
	item := map[string]types.AttributeValue{}
	item[string(KEY_DRUGS)] = &types.AttributeValueMemberL{Value: []types.AttributeValue{}}
	drugList := &(item[string(KEY_DRUGS)].(*types.AttributeValueMemberL).Value)
	for key, value := range relationships {
		// It is assumed that the relationships keys are in the format "KEY[i]: "
		// the [i] part is optional. It appears only if it is a series of values.
		// We remove the ": " part to simplify the storage to dynamodb.
		tableKey := strings.Trim(key, ": ")

		// Couples each prescribed drug with its frequency and aggregate the couples in a
		// list. All other keys are stored with their respective values as is.
		// It is assumed that the drug name key is "DRUGi" and the frequency key
		// is "FREQUENCYi", where i is the index of the drug in the prescription
		if tableKey[:len(tableKey)-1] == string(KEY_DRUG) {
			*drugList = append(*drugList, &types.AttributeValueMemberM{
				Value: map[string]types.AttributeValue{
					string(KEY_DRUG):      &types.AttributeValueMemberS{Value: strings.Trim(value, " ")},
					string(KEY_FREQUENCY): &types.AttributeValueMemberS{Value: strings.Trim(relationships[string(KEY_FREQUENCY)+key[len(key)-3:]], " ")},
				},
			})
		} else if !strings.Contains(tableKey, string(KEY_FREQUENCY)) {
			item[tableKey] = &types.AttributeValueMemberS{Value: strings.Trim(value, " ")}
		}
	}
	// add primary key to key-value pairs
	item[string(KEY_ID)] = &types.AttributeValueMemberS{Value: prescriptionId}

	// adds the prescription expiration date timestamp (seconds from epoch)
	// in order to allow for easy filtering of outdated prescriptions
	expirationDate, err := time.Parse(DATE_FORMAT, item[string(KEY_DATE)].(*types.AttributeValueMemberS).Value)
	if err != nil {
		log.Warn(fmt.Sprintf("couldn't parse prescription expiration date %s: %s", item[string(KEY_DATE)], err))
	} else {
		item[string(KEY_DATE_TIMESTAMPED)] = &types.AttributeValueMemberN{Value: fmt.Sprintf("%d", toTimestamp(expirationDate))}
	}

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

func LoadPrescribedDrugs(patientName string) ([]*PrescribedDrug, error) {

	prescribedDrugs := []*PrescribedDrug{}

	// creates a default client for dynamodb
	client, err := newDynamoDBClient()
	if err != nil {
		log.Error(err)
		return nil, fmt.Errorf("couldn't create dynamodb client")
	}

	// load all non-outdated prescription analysises from dynamodb of given patient
	// A prescription is outdated if its expiration date is strictly before today.
	// It is assumed that the expiration date is stored in the DATE key and that
	// it is formatted as specified in DATE_FORMAT.
	tableName := string(PRESCRIPTION_ANALYSIS)
	projectionExpression := string(KEY_DRUGS)
	filterExpression := fmt.Sprintf(
		"%s = %s AND %s >= %s",
		KEY_PATIENT.toExpressionAttributeName(),
		KEY_PATIENT.toExpressionAttributeValue(),
		KEY_DATE.toExpressionAttributeName(),
		KEY_DATE.toExpressionAttributeValue(),
	)
	log.Debug(filterExpression)
	request := &dynamodb.ScanInput{
		TableName:            &tableName,
		ProjectionExpression: &projectionExpression,
		FilterExpression:     &filterExpression,
		ExpressionAttributeValues: map[string]types.AttributeValue{
			KEY_PATIENT.toExpressionAttributeValue(): &types.AttributeValueMemberS{Value: patientName},
			KEY_DATE.toExpressionAttributeValue():    &types.AttributeValueMemberS{Value: time.Now().Format(DATE_FORMAT)},
		},
		ExpressionAttributeNames: map[string]string{
			KEY_PATIENT.toExpressionAttributeName(): string(KEY_PATIENT),
			KEY_DATE.toExpressionAttributeName():    string(KEY_DATE),
		},
	}

	// iterate over paginated response
	for {
		response, err := client.Scan(context.TODO(), request)
		if err != nil {
			log.Error(err)
			return nil, fmt.Errorf("error encountered after receiving a response from dynamodb ")
		}
		// parse response extracting prescribed drugs name and frequency
		for _, item := range response.Items {
			drugList := &(item[string(KEY_DRUGS)].(*types.AttributeValueMemberL).Value)
			for _, prescribedDrugItem := range *drugList {
				prescribedDrug := new(PrescribedDrug)
				prescribedDrug.Name = prescribedDrugItem.(*types.AttributeValueMemberM).Value[string(KEY_DRUG)].(*types.AttributeValueMemberS).Value
				prescribedDrug.Frequency = prescribedDrugItem.(*types.AttributeValueMemberM).Value[string(KEY_FREQUENCY)].(*types.AttributeValueMemberS).Value
				prescribedDrugs = append(prescribedDrugs, prescribedDrug)
			}
		}
		// request next page if there is one
		if len(response.LastEvaluatedKey) == 0 {
			break
		}
		request.ExclusiveStartKey = response.LastEvaluatedKey
	}

	return prescribedDrugs, nil

}
