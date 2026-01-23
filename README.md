# Ditto - The Sovereign Court

A private space for Chris & Annie, powered by React + Vite + Firebase.

## Local Development

```bash
npm install
npm run dev
```

## Setting Firebase Configuration

To enable Firebase features, set the `FIREBASE_CONFIG` repository secret with your Firebase configuration as a JSON string:

```json
{
  "apiKey": "...",
  "authDomain": "...",
  "projectId": "...",
  "storageBucket": "...",
  "messagingSenderId": "...",
  "appId": "..."
}
```

The GitHub Actions workflow will automatically inject this configuration at build time.

## Deployment

The app automatically deploys to GitHub Pages when changes are pushed to the `main` branch.

Visit: https://FenceHole.github.io/Ditto

