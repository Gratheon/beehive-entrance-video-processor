package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"time"
)

const gateVideoStreamURL = "http://localhost:8900/graphql"

// Structs to hold JSON response from services

// Struct to hold the response from the GraphQL service
type FetchNextUnprocessedVideoSegmentResponse struct {
	Data struct {
		FetchNextUnprocessedVideoSegment VideoSegment `json:"fetchNextUnprocessedVideoSegment"`
	} `json:"data"`
}
type VideoSegment struct {
	Id  string `json:"id"`
	URL string `json:"URL"`
}

// Struct to hold the inference results
type InferenceResult struct {
	BeesIn      int `json:"beesIn"`
	BeesOut     int `json:"beesOut"`
	VarroaCount int `json:"varroaCount"`
	WespenCount int `json:"wespenCount"`
	PollenCount int `json:"pollenCount"`
}

func main() {
	// Create a ticker that ticks every 10 seconds
	ticker := time.NewTicker(10 * time.Second)
	defer ticker.Stop()

	// Infinite loop to continuously fetch new jobs
	for {
		select {
		case <-ticker.C:
			// Fetch new job every tick
			if err := processJob(); err != nil {
				fmt.Println("Error processing job:", err)
			}
		}
	}
}

func processJob() error {
	// Make request to remote service over HTTP & GraphQL to fetch video URL
	videoSegment, err := fetchVideoURL()
	fmt.Printf("%v", videoSegment)

	if err != nil {
		return fmt.Errorf("error fetching video URL: " + err.Error())
	}

	// Download the video file
	if err := downloadVideo(videoSegment.Id, videoSegment.URL); err != nil {
		return fmt.Errorf("error downloading video file: %w", err)
	}

	// // Get inference results
	// inferenceResult, err := getInferenceResults()
	// if err != nil {
	//     return fmt.Errorf("error getting inference results: %w", err)
	// }

	// Post inference results to the first service
	if err := postInferenceResults(videoSegment.Id,
		&InferenceResult{
			BeesIn:      10,
			BeesOut:     20,
			VarroaCount: 30,
			WespenCount: 40,
			PollenCount: 50,
		},
	); err != nil {
		return fmt.Errorf("error posting inference results: %w", err)
	}

	fmt.Println("Processing complete.")
	return nil
}

func fetchVideoURL() (*VideoSegment, error) {
	// Prepare the request body
	requestBody := []byte(`{"query": "query { fetchNextUnprocessedVideoSegment { id URL } }"}`)

	// Create a new HTTP request
	req, err := http.NewRequest("POST", gateVideoStreamURL, bytes.NewBuffer(requestBody))
	if err != nil {
		return nil, err
	}

	// Set the Content-Type header
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("internal-userid", "1")

	// Make the HTTP request
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	// Log response
	fmt.Printf("response: %v\n", resp.Body)

	// Parse the response
	var response FetchNextUnprocessedVideoSegmentResponse
	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, err
	}

	return &response.Data.FetchNextUnprocessedVideoSegment, nil
}

func downloadVideo(id string, videoURL string) error {
	// Create a directory to store downloaded videos if it doesn't exist
	err := os.MkdirAll(filepath.Join(".", "tmp"), os.ModePerm)
	if err != nil {
		return err
	}

	// Create a file to save the video
	outputPath := filepath.Join(".", "tmp", id+".mp4")
	outputFile, err := os.Create(outputPath)
	if err != nil {
		return err
	}
	defer outputFile.Close()

	// Make HTTP GET request to download the video
	resp, err := http.Get(videoURL)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	// Check if the response status code is OK
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("failed to download: %s", resp.Status)
	}

	// Copy the response body to the file
	bytesWritten, err := io.Copy(outputFile, resp.Body)
	if err != nil {
		return err
	}

	fmt.Printf("Downloaded %d bytes\n", bytesWritten)

	return nil
}

func getInferenceResults() (InferenceResult, error) {
	// Implement logic to get inference results
	// Make HTTP request to another service to get the inference results
	// You may use libraries like "net/http" for this
	return InferenceResult{}, nil
}

type UpdateDetectionStatsGQLRequest struct {
	Id             string          `json:"id"`
	DetectionStats InferenceResult `json:"detectionStats"`
}

func postInferenceResults(videoSegmentId string, result *InferenceResult) error {
	// Define the GraphQL mutation query with variables
	query := `mutation UpdateDetectionStats($id: ID!, $detectionStats: DetectionStats!) {
			updateVideoSegmentDetectionStats(id: $id, detectionStats: $detectionStats)
		}`

	// Encode the GraphQL variables into JSON bytes
	variablesData, err := json.Marshal(&UpdateDetectionStatsGQLRequest{
		Id:             videoSegmentId,
		DetectionStats: *result,
	})
	if err != nil {
		return err
	}

	// Compose the final GraphQL request payload
	requestPayload := fmt.Sprintf(`{"operationName":"UpdateDetectionStats", "query": %q, "variables": %s}`, query, string(variablesData))

	// Create a new HTTP request with the GraphQL query as the body
	req, err := http.NewRequest("POST", gateVideoStreamURL, bytes.NewBuffer([]byte(requestPayload)))
	if err != nil {
		return err
	}

	// Set the Content-Type header to application/json
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("internal-userid", "1")

	// Make the HTTP request
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	// print body
	fmt.Printf("response: %v\n", resp.Body)

	// Check the response status
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("unexpected status code: %d", resp.StatusCode)
	}

	return nil
}
