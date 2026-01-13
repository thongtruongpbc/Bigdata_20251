from processor import processor
import argparse
import time
import os
from feast.data_source import PushMode

def main(args):
    if args.mode == "setup":
        print(f"--- Starting Stream Ingestion to {args.store} store ---")
        
        # Kích hoạt Spark Streaming Query thông qua Feast Processor
        if args.store == "online":
            query = processor.ingest_stream_feature_view()
        elif args.store == "offline":
            query = processor.ingest_stream_feature_view(PushMode.OFFLINE)
        else:
            raise ValueError("Invalid store! Please select online or offline")
        
        try:
            # awaitTermination() duy trì session và in log Spark ra terminal
            query.awaitTermination()
        except KeyboardInterrupt:
            print("\n--- Stopping Stream Ingestion ---")
            query.stop()

    elif args.mode == "teardown":
        print("Teardown mode initiated.")
    else:
        raise ValueError("Invalid mode! Please select setup or teardown")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest stream to stores.")
    parser.add_argument("-m", "--mode", default="setup", help="setup or teardown")
    parser.add_argument("-s", "--store", default="online", help="online or offline")
    args = parser.parse_args()
    main(args)