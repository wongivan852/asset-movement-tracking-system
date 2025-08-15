# Asset Movement Tracking System

A comprehensive Django web application for tracking valuable assets moving between Hong Kong and Shenzhen locations, providing real-time visibility and accountability for asset movements.

## 🚀 Features

### Core Functionality
- **User Management**: Role-based access with administrators, location managers, and personnel
- **Asset Registry**: Comprehensive asset management with unique identifiers, categories, and detailed specifications
- **Location Management**: Support for multiple locations (Hong Kong, Shenzhen) with extensibility for additional venues
- **Movement Tracking**: Real-time asset movement tracking between locations with unique tracking numbers
- **Reception & Acknowledgement**: Asset receipt confirmation system with condition reporting
- **Remarks System**: Timestamped notes and comments for asset lifecycle tracking
- **Stock Taking**: Physical inventory management and verification
- **Dashboard**: Real-time status monitoring and reporting
- **Audit Trail**: Complete activity logging for accountability
- **Notifications**: Alerts for overdue items and pending actions

### Technical Features
- **Responsive Design**: Mobile-friendly interface using Bootstrap 5
- **Real-time Charts**: Asset status visualization using Chart.js
- **PostgreSQL Ready**: Production-ready database configuration
- **Security**: Comprehensive user authentication and authorization
- **Performance Optimized**: Database indexing and query optimization
- **Extensible**: Modular architecture for easy feature additions

## 📋 Requirements

Based on the requirements document, this system addresses all specified needs:

1. ✅ **User Management** - Role-based access control
2. ✅ **Asset Management** - Comprehensive asset registry
3. ✅ **Location Management** - Hong Kong & Shenzhen locations
4. ✅ **Movement Tracking** - Complete movement lifecycle
5. ✅ **Asset Reception** - Acknowledgement system
6. ✅ **Remarks System** - Timestamped notes
7. ✅ **Stock Taking** - Inventory management
8. ✅ **Real-time Dashboard** - Status monitoring
9. ✅ **Reporting** - Comprehensive reports
10. ✅ **Notifications** - Alert system

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Quick Start

1. **Clone the repository** (if applicable):
   ```bash
   git clone <repository-url>
   cd company_asset_management
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install django psycopg2-binary python-decouple django-bootstrap5 django-crispy-forms crispy-bootstrap5
   ```

4. **Environment Configuration**:
   Copy `.env.example` to `.env` and update the settings:
   ```bash
   cp .env.example .env
   ```

5. **Database Setup**:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py populate_data  # Load sample data
   ```

6. **Run the application**:
   ```bash
   python manage.py runserver
   ```

7. **Access the application**:
   Open your browser and navigate to `http://127.0.0.1:8000`

## 👥 Default Users

The system comes with pre-configured demo users:

| Username | Password | Role | Description |
|----------|----------|------|-------------|
| `admin` | `password` | Administrator | Full system access |
| `manager` | `password` | Location Manager | Location and staff management |
| `staff` | `password` | Personnel | Basic asset operations |

## 📱 User Interface

### Dashboard
- Real-time asset statistics
- Recent movements overview
- Alert notifications
- Quick action buttons
- Status distribution charts

### Asset Management
- Comprehensive asset registry
- Detailed asset information
- Category management
- Search and filtering
- Asset history tracking

### Movement Tracking
- Create new movements
- Track asset locations
- Movement acknowledgements
- Status updates
- Overdue monitoring

### Stock Taking
- Schedule inventory checks
- Record findings
- Track discrepancies
- Generate reports

## 🗃️ Database Schema

### Key Models

#### User (Custom User Model)
- Extended Django User with role-based access
- Roles: Admin, Location Manager, Personnel
- Additional fields: phone, department, employee_id

#### Asset
- Unique asset identification
- Category classification
- Financial information (purchase/current value)
- Location tracking
- Status management (available, in_transit, in_use, maintenance, retired)

#### Location
- Location details (name, address, contact)
- Responsible personnel
- Asset associations

#### Movement
- Asset movement tracking
- From/to locations
- Status progression
- Acknowledgement system
- Audit trail

#### Stock Take
- Inventory verification
- Location-based stock takes
- Item-by-item verification
- Discrepancy tracking

## 🔧 Configuration

### Environment Variables
- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `DATABASE_URL`: Database connection string
- `TIME_ZONE`: System timezone (default: Asia/Hong_Kong)

### Database Configuration
- Development: SQLite (default)
- Production: PostgreSQL (recommended)

## 🚀 Deployment

### Production Checklist
1. Set `DEBUG=False` in environment
2. Configure PostgreSQL database
3. Set up proper SECRET_KEY
4. Configure ALLOWED_HOSTS
5. Set up static file serving
6. Configure email settings for notifications
7. Set up logging
8. Configure SSL/HTTPS

### Docker Deployment (Future Enhancement)
```dockerfile
# Dockerfile structure for containerized deployment
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "asset_tracker.wsgi:application"]
```

## 📊 API Endpoints

### Dashboard API
- `GET /dashboard/api/stats/` - Dashboard statistics

### Movement Tracking API
- `GET /movements/api/track/<tracking_number>/` - Track movement

## 🔒 Security Features

- **Authentication**: Required for all operations
- **Authorization**: Role-based access control
- **CSRF Protection**: Built-in Django protection
- **SQL Injection Protection**: ORM-based queries
- **XSS Protection**: Template auto-escaping
- **Password Policies**: Configurable validation
- **Session Management**: Secure session handling

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

## 📈 Performance Optimization

- Database indexing on frequently queried fields
- Query optimization using select_related and prefetch_related
- Pagination for large datasets
- Caching for dashboard statistics
- Static file compression

## 🔄 Future Enhancements

- [ ] Barcode/QR code scanning integration
- [ ] Mobile app for field operations
- [ ] Email notifications
- [ ] Advanced reporting with PDF export
- [ ] API for external system integration
- [ ] Real-time WebSocket updates
- [ ] Multi-language support
- [ ] Advanced analytics and insights

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is proprietary software developed for internal company use.

## 📞 Support

For support and maintenance:
- Internal IT Team: it-support@company.com
- Documentation: Available in the admin interface
- Training: Available upon request

## 🏗️ Architecture

### Project Structure
```
asset_tracker/
├── asset_tracker/          # Main project configuration
├── accounts/               # User management
├── assets/                 # Asset management
├── locations/              # Location management
├── movements/              # Movement tracking
├── dashboard/              # Dashboard and reporting
├── templates/              # HTML templates
├── static/                 # Static files (CSS, JS, images)
├── fixtures/               # Sample data
└── manage.py              # Django management script
```

### Key Technologies
- **Backend**: Django 4.2, Python 3.8+
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Frontend**: Bootstrap 5, Chart.js, Font Awesome
- **Authentication**: Django built-in auth
- **Forms**: Django Crispy Forms with Bootstrap 5

---

**Asset Movement Tracking System** - Built with ❤️ for efficient asset management between Hong Kong and Shenzhen locations.
