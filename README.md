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

- `web/` - Responsive web frontend
  - `index.html` - Main HTML structure with form and display areas
  - `styles.css` - Mobile-first responsive styling
  - `app.js` - Frontend logic and API integration

## Features

- Responsive design optimized for both desktop and mobile devices
- Secure credential handling through HTTPS
- Real-time loading indicators and error feedback
- Markdown rendering of workout summaries
- One-click markdown copying functionality
- Touch-optimized for mobile devices

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
     ```json
     {
       "email": "your.garmin.email@example.com",
       "password": "your-garmin-password"
     }
     ```
   - Credentials are only used for the request and are not stored

4. Deploy the web frontend:
   - Update the API endpoint URL in `web/app.js`
   - Host the web files on your preferred static hosting service (e.g., AWS S3)
   - Configure CORS in the API Gateway to allow requests from your hosting domain

5. Usage:
   - Visit the web frontend
   - Enter your Garmin Connect credentials
   - Click "Retrieve Workouts" to fetch and display your previous week's training data
   - Use "Copy Markdown" to copy the formatted summary

## Development

To run locally:

1. Clone the repository
2. Install dependencies per Setup instructions above
3. Run SAM locally:
   ```
   sam local start-api
   ```
4. Serve the web frontend using a local server:
   ```
   python -m http.server 8000
   ```
5. Open `http://localhost:8000` in your browser

## Security Notes

- The Lambda function uses IAM roles with minimal required permissions
- API Gateway endpoints use HTTPS
- Credentials are transmitted securely and not stored
- Frontend implements secure practices for handling sensitive data

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

