# Garmin Connect Weekly Summary Generator

This project provides an automated way to generate weekly training summaries from Garmin Connect data. It fetches activities from the previous week and calculates various metrics including:

- Activity counts, durations and distances
- Pace calculations for running and swimming 
- Efficiency Factor (EF) calculations for running and cycling
- Weekly totals and averages

## Components

The project consists of:

- `api/` - AWS Lambda function and API Gateway endpoint
  - `handler.py` - Main Lambda handler with activity processing logic
  - `template.yaml` - SAM template for AWS deployment
  - `requirements.txt` - Python dependencies

- `web/` - Simple web frontend
  - `styles.css` - Basic styling

## Setup

1. Install dependencies:
   ```
   cd api
   pip install -r requirements.txt
   ```

2. Configure AWS credentials and SAM CLI:
   - Install AWS SAM CLI
   - Configure AWS credentials with appropriate permissions
   - Run `sam build` and `sam deploy` to deploy the Lambda function

3. Using the API:
   - Send a POST request to the API endpoint with your Garmin credentials:
     ```
     {
       "email": "your.garmin.email@example.com",
       "password": "your-garmin-password"
     }
     ```
   - Credentials are only used for the request and are not stored

4. Deploy the web frontend:
   - Host the web files on your preferred static hosting service
   - Update the API endpoint URL in the frontend code to point to your deployed Lambda function

5. Usage:
   - Visit the web frontend
   - Click "Generate Summary" to fetch and display your previous week's training data
   - The summary will show activities grouped by day with calculated metrics

## Development

To run locally:

1. Clone the repository
2. Install dependencies per Setup instructions above
3. Run SAM locally:
   ```
   sam local start-api
   ```
4. Open the web frontend in your browser

## Security Notes

- The Lambda function uses IAM roles with minimal required permissions
- API Gateway endpoints use HTTPS

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

