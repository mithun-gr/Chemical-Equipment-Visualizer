# Chemical Equipment Parameter V visualizer

A hybrid web + desktop application for analyzing chemical equipment data. Built for FOSSEE Intern Screening Task.

## 🎯 Features

- **CSV Upload**: Upload equipment data via web or desktop app
- **Data Visualization**: Charts showing equipment type distribution and parameters
- **Summary Statistics**: Calculate averages for flowrate, pressure, and temperature
- **History Management**: Track last 5 uploads
- **PDF Reports**: Generate downloadable reports
- **Authentication**: Secure login system
- **Hybrid Support**: Both web (React) and desktop (PyQt5) applications

## 🛠 Tech Stack

### Backend

- Django 4.2
- Django REST Framework
- SQLite Database
- Token Authentication

### Web Frontend

- React
- Chart.js for charts
- Basic CSS styling

### Desktop Frontend

- PyQt5
- Matplotlib for charts
- Requests library

## 📁 Project Structure

```
chemical-equipment-visualizer/
├── backend/              # Django REST API
│   ├── api/             # Main app
│   ├── equipment_api/   # Project settings
│   ├── manage.py
│   ├── requirements.txt
│   └── db.sqlite3
├── frontend/            # React web app
│   ├── src/
│   ├── public/
│   └── package.json
├── desktop_app/         # PyQt5 desktop app
│   ├── main.py
│   ├── login_window.py
│   ├── main_window.py
│   └── requirements.txt
├── sample_data.csv      # Sample CSV file
└── README.md
```

## 🚀 Setup Instructions

### Backend Setup

1. Navigate to backend directory:

```bash
cd backend
```

2. Create virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run migrations:

```bash
python manage.py migrate
```

5. Start server:

```bash
python manage.py runserver
```

Backend will run on `http://localhost:8000`

### Web Frontend Setup

1. Navigate to frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Start development server:

```bash
npm start
```

Web app will open on `http://localhost:3000`

### Desktop App Setup

1. Navigate to desktop_app directory:

```bash
cd desktop_app
```

2. Create virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run application:

```bash
python main.py
```

## 📝 API Endpoints

| Method | Endpoint               | Description                    |
| ------ | ---------------------- | ------------------------------ |
| POST   | `/api/register/`       | User registration              |
| POST   | `/api/login/`          | User login (returns token)     |
| POST   | `/api/upload_csv/`     | Upload CSV file                |
| GET    | `/api/summary/<id>/`   | Get summary for upload session |
| GET    | `/api/equipment/<id>/` | Get equipment list             |
| GET    | `/api/history/`        | Get last 5 uploads             |
| GET    | `/api/charts/<id>/`    | Get chart data                 |
| GET    | `/api/pdf/<id>/`       | Generate PDF report            |

## 📊 Sample Data Format

CSV file should have these columns:

- Equipment Name
- Type
- Flowrate
- Pressure
- Temperature

Example:

```csv
Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-1,Pump,120,5.2,110
Compressor-1,Compressor,95,8.4,95
```

## 🎨 Features Implementation

### CSV Upload

- Validates CSV structure
- Parses data using Python csv module
- Stores in SQLite database
- Calculates summary statistics

### Data Visualization

- **Web**: Chart.js bar and pie charts
- **Desktop**: Matplotlib embedded plots
- Shows equipment type distribution
- Parameter comparisons

### Authentication

- Django Token Authentication
- Token stored in localStorage (web)
- Token stored globally (desktop)

### PDF Generation

- Returns HTML that can be printed to PDF
- Includes summary statistics
- Equipment type distribution table
- Full equipment details

## 🧪 Testing

1. **Backend**: Start Django server and test API with curl/Postman
2. **Web**: Run `npm start` and test upload flow
3. **Desktop**: Run `python main.py` and test all features

Test with provided `sample_data.csv` file.

## 🎓 Challenges Faced & Learning

- **Pandas dependency issues**: Switched to Python csv module for simpler approach
- **PDF generation**: Used HTML response instead of complex libraries
- **CORS setup**: Configured for development allowing all origins
- **Token authentication**: Implemented simple token-based auth
- **Chart integration**: Learned Chart.js for web, Matplotlib for desktop

## ⚡ Future Improvements

- Add data filtering and search
- Export to Excel
- More chart types (line charts for trends)
- User profile management
- Deployment to cloud (Heroku/Railway)
- Add unit tests
- Improve error handling
- Add data validation rules

## 👨‍💻 Author

Built by [Your Name] for FOSSEE Intern Screening Task

## 📄 License

This project was created for internship screening purposes.

## 🔗 Demo

- **GitHub Repository**: https://github.com/mithun-gr/Chemical-Equipment-Visualizer
- **Demo Video**: [Add your video link]
- **Deployed Web App** (Optional): [Add deployment link]
