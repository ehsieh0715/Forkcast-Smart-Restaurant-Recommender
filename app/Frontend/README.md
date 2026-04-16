# 🍴 Forkcast

## 📚 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Folder Structure](#-folder-structure)
- [Folder and File Purposes](#-folder-and-file-purpose)
- [Application Routes](#-application-routes)
- [Environment Variables](#-environment-variables)
- [Contributing](#-contributing)

## 🚀 Features

- Solo (Personal) restaurant recommendation system
- Group-based recommendation sessions with consensus scoring
- Full-fit score calculation for multi-user group matching
- Heatmap backend API for city-wide busyness visualization
- Dynamic restaurant comparison module (session-based)

## ⚙️ Tech Stack

[![My Skills](https://skillicons.dev/icons?i=react,tailwind,figma,html,css,js,mui,postman,vite,vscode)](https://skillicons.dev)

## 🛠️ Installation

To run this project locally, follow these steps:

```bash
# 1. Clone the repository
git clone https://github.com/Justetete/COMP47360_Summer_Project_Group5.git
```

```bash
# 2. Navigate into the project directory
cd COMP47360_Summer_Project_Group5/app/Frontend
```

```bash
# 3. Install dependencies
npm install
```

```bash
# 4. Start the development server
npm run dev
```

## 🗒️ Folder Structure

```bash
📦Frontend
 ┣ 📂public
 ┃ ┣ 📜fork.svg
 ┃ ┣ 📜Forkcast.svg
 ┃ ┣ 📜form-graphic.svg
 ┃ ┣ 📜homepage.svg
 ┃ ┣ 📜homepage2.svg
 ┃ ┣ 📜LandingpageRestaurant.jpg
 ┃ ┣ 📜loginpage.jpg
 ┃ ┣ 📜no-image.jpg
 ┃ ┣ 📜page-not-found.svg
 ┃ ┗ 📜Quitebite.png
 ┣ 📂src
 ┃ ┣ 📂components
 ┃ ┃ ┣ 📜Auth.jsx
 ┃ ┃ ┣ 📜Checkbox.jsx
 ┃ ┃ ┣ 📜ComparisonCard.jsx
 ┃ ┃ ┣ 📜ComparisonPageContent.jsx
 ┃ ┃ ┣ 📜ComparisonPageHeader.jsx
 ┃ ┃ ┣ 📜FeatureCard.jsx
 ┃ ┃ ┣ 📜Footer.jsx
 ┃ ┃ ┣ 📜GroupPageContent.jsx
 ┃ ┃ ┣ 📜GroupPageHeader.jsx
 ┃ ┃ ┣ 📜GroupRestaurantCard.jsx
 ┃ ┃ ┣ 📜HomePageHeader.jsx
 ┃ ┃ ┣ 📜HomePageRestaurantCard.jsx
 ┃ ┃ ┣ 📜LandingPageContent.jsx
 ┃ ┃ ┣ 📜LandingPageFeatures.jsx
 ┃ ┃ ┣ 📜LandingPageHeader.jsx
 ┃ ┃ ┣ 📜LeafletMap.jsx
 ┃ ┃ ┣ 📜LineChart.jsx
 ┃ ┃ ┣ 📜LoginGoogle.jsx
 ┃ ┃ ┣ 📜Map.jsx
 ┃ ┃ ┣ 📜MapboxMap.jsx
 ┃ ┃ ┣ 📜Modal.jsx
 ┃ ┃ ┣ 📜Navbar.jsx
 ┃ ┃ ┣ 📜PreferenceDisplay.jsx
 ┃ ┃ ┣ 📜ProfileContent.jsx
 ┃ ┃ ┣ 📜RadarChart.jsx
 ┃ ┃ ┣ 📜RestaurantActions.jsx
 ┃ ┃ ┣ 📜RestaurantAmenities.jsx
 ┃ ┃ ┣ 📜RestaurantAnalyticsPanel.jsx
 ┃ ┃ ┣ 📜RestaurantBasic.jsx
 ┃ ┃ ┣ 📜RestaurantCard.jsx
 ┃ ┃ ┣ 📜RestaurantCrowdForecast.jsx
 ┃ ┃ ┣ 📜RestaurantDetailsContent.jsx
 ┃ ┃ ┣ 📜RestaurantDetailsHeader.jsx
 ┃ ┃ ┣ 📜RestaurantSearchDropdown.jsx
 ┃ ┃ ┣ 📜RestaurantWaittimes.jsx
 ┃ ┃ ┗ 📜SidebarFilters.jsx
 ┃ ┣ 📂context
 ┃ ┃ ┣ 📜GroupRecommendationContext.jsx
 ┃ ┃ ┣ 📜HeatmapContext.jsx
 ┃ ┃ ┣ 📜LocationContext.jsx
 ┃ ┃ ┣ 📜RestaurantContext.jsx
 ┃ ┃ ┗ 📜SoloRecommendationContext.jsx
 ┃ ┣ 📂hooks
 ┃ ┃ ┗ 📜useMediaQuery.jsx
 ┃ ┣ 📂pages
 ┃ ┃ ┣ 📜ComparisonPage.jsx
 ┃ ┃ ┣ 📜ErrorPage.jsx
 ┃ ┃ ┣ 📜GroupPage.jsx
 ┃ ┃ ┣ 📜HomePage.jsx
 ┃ ┃ ┣ 📜LandingPage.jsx
 ┃ ┃ ┣ 📜LoginPage.jsx
 ┃ ┃ ┣ 📜Logout.jsx
 ┃ ┃ ┣ 📜NavbarRootPage.jsx
 ┃ ┃ ┣ 📜OnboardingPage.jsx
 ┃ ┃ ┣ 📜ProfilePage.jsx
 ┃ ┃ ┣ 📜RestaurantDetails.jsx
 ┃ ┃ ┣ 📜RootPage.jsx
 ┃ ┃ ┣ 📜SignupPage.jsx
 ┃ ┃ ┗ 📜SoloPage.jsx
 ┃ ┣ 📂utils
 ┃ ┃ ┣ 📜BackdropLoader.jsx
 ┃ ┃ ┣ 📜DistanceCalculator.jsx
 ┃ ┃ ┣ 📜ScrollToTop.jsx
 ┃ ┃ ┗ 📜Session.jsx
 ┃ ┣ 📜App.css
 ┃ ┣ 📜App.jsx
 ┃ ┣ 📜index.css
 ┃ ┗ 📜main.jsx
 ┣ 📜.env
 ┣ 📜.env.production
 ┣ 📜.gitignore
 ┣ 📜.prettierrc
 ┣ 📜Dockerfile
 ┣ 📜eslint.config.js
 ┣ 📜index.html
 ┣ 📜nginx.conf
 ┣ 📜package-lock.json
 ┣ 📜package.json
 ┣ 📜README.md
 ┗ 📜vite.config.js
```

### 📑 Folder and File Purposes

| Folder / File     | Purpose / Description                                                                  |
| ----------------- | -------------------------------------------------------------------------------------- |
| `public/`         | Contains static assets like images and SVGs that are served directly by the browser.   |
| `src/App.jsx`     | Main application component. Sets up routing and renders the overall app structure.     |
| `src/components/` | Reusable UI components like cards, navbars, charts, and forms used throughout the app. |
| `src/context/`    | React context providers for managing global state like user sessions or map data.      |
| `src/hooks/`      | Custom React hooks for reusable logic, e.g., responsive design or data fetchers.       |
| `src/pages/`      | Page-level React components that map to routes, like Home, Login, Profile, etc.        |
| `src/utils/`      | Utility functions and helper components, e.g., loaders, distance calculators, etc.     |

## 🌐 Application Routes

The app uses `react-router` with nested route structures and data loaders for auth checks and data fetching.

| Path               | Component        | Purpose                                            | Protected |
| ------------------ | ---------------- | -------------------------------------------------- | --------- |
| `/`                | `LandingPage`    | Default landing page (shown if not authenticated). | ❌        |
| `/home`            | `HomePage`       | Main homepage for authenticated users.             | ✅        |
| `/solo`            | `SoloPage`       | Restaurant recommendation page for solo users.     | ✅        |
| `/group`           | `GroupPage`      | Group-based restaurant recommendation flow.        | ✅        |
| `/onboarding`      | `OnboardingPage` | Onboarding flow after sign-up.                     | ✅        |
| `/profile`         | `ProfilePage`    | User profile and preferences.                      | ✅        |
| `/compare`         | `ComparisonPage` | Comparison view for selected restaurants.          | ✅        |
| `/login`           | `LoginPage`      | Entry point for login (Google or password).        | ❌        |
| `/login/google`    | —                | Auth route for Google login.                       | ❌        |
| `/login/password`  | —                | Auth route for email/password login.               | ❌        |
| `/signup`          | `SignupPage`     | Entry point for sign-up (Google or password).      | ❌        |
| `/signup/google`   | —                | Auth route for Google sign-up.                     | ❌        |
| `/signup/password` | —                | Auth route for email/password sign-up.             | ❌        |
| `/logout`          | —                | Triggers user logout and redirects.                | ✅        |
| `\*`(fallback)     | `ErrorPage`      | Handles all unknown routes with an error display.  | ❌        |

## 🔐 Environment Variables

Set the following environment variable in a `.env` file at the root of the frontend:

```bash
VITE_API_URL=  # 🔗 Set this to your backend's IP address and port
```

## 🤝 Contributing

- Bingzheng Lyu
- Xiaoxia Jin
- Wan-Hua Hsieh
- Xinchi Jian
- Eli Young
- Aadhithya Ganesh
