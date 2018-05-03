// Sample speech-quickstart uses the Google Cloud Speech API to transcribe
// audio.
package main

import (
	"context"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"path/filepath"

	"github.com/go-audio/wav"

	speech "cloud.google.com/go/speech/apiv1"
	speechpb "google.golang.org/genproto/googleapis/cloud/speech/v1"
)

func main() {
	if len(os.Args) <= 1 {
		fmt.Print("Please provide audio file path to transcribe as an argument. Usage: transcription <filename>")
		return
	}

	ctx := context.Background()

	var sendFunc func(*speech.Client, string) (*speechpb.LongRunningRecognizeResponse, error)

	path := os.Args[1]
	filename := filepath.Base(path)
	pathToUse := path

	//verify path exists
	if _, err := os.Stat(path); os.IsNotExist(err) {
		log.Printf("%v does not exit", path)
		return
	}

	//get duration of wav file
	f, err := os.Open(path)
	if err != nil {
		log.Fatal(err)
		return
	}
	defer f.Close()
	dur, err := wav.NewDecoder(f).Duration()
	if err != nil {
		log.Fatal(err)
		return
	}

	//determine which transcription method to use
	if dur.Seconds() > 60 {
		log.Printf("using google cloud storage for %v because it is %v seconds", filename, dur.Seconds())

		//get the GCS bucket id
		b, err := ioutil.ReadFile("../credentials/cloudstoragebucket.txt")
		if err != nil {
			log.Fatalf("Cloud storage bucket for use must be defined in credentials/cloudstoragebucket.txt: %v", err)
		}
		gcsBucketName := string(b)
		gcspath := "gs://" + gcsBucketName + "/" + filename

		cloudstorage("ezuce-transcription-voicemail", path, filename, "write")
		pathToUse = gcspath
		sendFunc = sendGCS
	} else {
		log.Printf("just posting audio file in transcription request for %v because it is %v seconds", filename, dur.Seconds())
		sendFunc = send
	}

	// Creates a speech client.
	client, err := speech.NewClient(ctx)
	if err != nil {
		log.Fatalf("Failed to create client: %v", err)
	}

	//run transcription
	resp, err := sendFunc(client, pathToUse)
	if err != nil {
		deleteGCSVM(path, filename)
		log.Fatalf("failed to transcribe: %v", err)
		return
	}

	// Prints the results.
	for _, result := range resp.Results {
		for _, alt := range result.Alternatives {
			//fmt.Printf("\"%v\" (confidence=%3f)\n", alt.Transcript, alt.Confidence)
			fmt.Printf("%v", alt.Transcript)
		}
	}
	deleteGCSVM(path, filename)
}

func deleteGCSVM(path string, filename string) {
	cloudstorage("ezuce-transcription-voicemail", path, filename, "delete")
}

//send a file (has to be <1min)
func send(client *speech.Client, filename string) (*speechpb.LongRunningRecognizeResponse, error) {
	ctx := context.Background()
	data, err := ioutil.ReadFile(filename)
	if err != nil {
		return nil, err
	}

	// Send the contents of the audio file with the encoding and
	// and sample rate information to be transcripted.
	req := &speechpb.LongRunningRecognizeRequest{
		Config: &speechpb.RecognitionConfig{
			Encoding:        speechpb.RecognitionConfig_LINEAR16,
			SampleRateHertz: 16000,
			LanguageCode:    "en-US",
		},
		Audio: &speechpb.RecognitionAudio{
			AudioSource: &speechpb.RecognitionAudio_Content{Content: data},
		},
	}

	op, err := client.LongRunningRecognize(ctx, req)
	if err != nil {
		log.Fatalf("failed to iniate long running transcription client: %v", err)
	}
	return op.Wait(ctx)
}

func sendGCS(client *speech.Client, gcsURI string) (*speechpb.LongRunningRecognizeResponse, error) {
	ctx := context.Background()

	// Send the contents of the audio file with the encoding and
	// and sample rate information to be transcripted.
	req := &speechpb.LongRunningRecognizeRequest{
		Config: &speechpb.RecognitionConfig{
			Encoding:        speechpb.RecognitionConfig_LINEAR16,
			SampleRateHertz: 16000,
			LanguageCode:    "en-US",
		},
		Audio: &speechpb.RecognitionAudio{
			AudioSource: &speechpb.RecognitionAudio_Uri{Uri: gcsURI},
		},
	}

	op, err := client.LongRunningRecognize(ctx, req)
	if err != nil {
		log.Fatalf("failed to iniate long running transcription client: %v", err)
		return nil, err
	}
	return op.Wait(ctx)
}
