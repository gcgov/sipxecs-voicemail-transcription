// Sample speech-quickstart uses the Google Cloud Speech API to transcribe
// audio.
package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"os"

	// Imports the Google Cloud Speech API client package.
	"golang.org/x/net/context"

	speech "cloud.google.com/go/speech/apiv1"
	speechpb "google.golang.org/genproto/googleapis/cloud/speech/v1"
)

func main() {
	if len(os.Args) <= 1 {
		fmt.Print("Please provide audio file path to transcribe as an argument. Usage: transcription <filename>")
		return
		//os.Exit(1)
	}

	ctx := context.Background()

	// Creates a client.
	client, err := speech.NewClient(ctx)
	if err != nil {
		log.Fatalf("Failed to create client: %v", err)
	}

	// Sets the name of the audio file to transcribe.
	//filename := "/path/to/audio.raw"
	filename := os.Args[1]

	if _, err := os.Stat(filename); os.IsNotExist(err) {
		fmt.Printf("%v does not exit", filename)
		return
	}

	// Reads the audio file into memory.
	data, err := ioutil.ReadFile(filename)
	if err != nil {
		log.Fatalf("Failed to read file: %v", err)
	}

	// Detects speech in the audio file.
	resp, err := client.Recognize(ctx, &speechpb.RecognizeRequest{
		Config: &speechpb.RecognitionConfig{
			Encoding: speechpb.RecognitionConfig_LINEAR16,
			//SampleRateHertz: 16000,
			LanguageCode: "en-US",
		},
		Audio: &speechpb.RecognitionAudio{
			AudioSource: &speechpb.RecognitionAudio_Content{Content: data},
		},
	})
	if err != nil {
		log.Fatalf("failed to recognize: %v", err)
	}

	// Prints the results.
	for _, result := range resp.Results {
		for _, alt := range result.Alternatives {
			//fmt.Printf("\"%v\" (confidence=%3f)\n", alt.Transcript, alt.Confidence)
			fmt.Printf("%v", alt.Transcript)
		}
	}
}
