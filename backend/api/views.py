from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Equipment, UploadSession
from .serializers import EquipmentSerializer, UploadSessionSerializer
import csv
import io
from django.http import HttpResponse


# Simple registration view
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')
    
    # basic validation
    if not username or not password:
        return Response({'error': 'Username and password required'}, 
                        status=status.HTTP_400_BAD_REQUEST)
    
    # check if user exists
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, 
                        status=status.HTTP_400_BAD_REQUEST)
    
    # create user
    user = User.objects.create_user(username=username, password=password, email=email)
    token, _ = Token.objects.get_or_create(user=user)
    
    return Response({
        'token': token.key,
        'user_id': user.id,
        'username': user.username
    }, status=status.HTTP_201_CREATED)


# Simple login view
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username
        })
    else:
        return Response({'error': 'Invalid credentials'}, 
                        status=status.HTTP_401_UNAUTHORIZED)


# CSV upload view - function based (easier to understand for beginners)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_csv(request):
    try:
        # get the uploaded file
        if 'file' not in request.FILES:
            return Response({'error': 'No file uploaded'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        csv_file = request.FILES['file']
        
        # Read CSV using Python csv module (simple approach)
        decoded_file = csv_file.read().decode('utf-8')
        csv_data = csv.DictReader(io.StringIO(decoded_file))
        
        # Convert to list to count rows
        rows = list(csv_data)
        
        # Basic validation - check required columns
        if len(rows) == 0:
            return Response({'error': 'Empty CSV file'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        required_columns = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
        first_row = rows[0]
        for col in required_columns:
            if col not in first_row:
                return Response({'error': f'Missing column: {col}'}, 
                                status=status.HTTP_400_BAD_REQUEST)
        
        # Create upload session
        session = UploadSession.objects.create(
            user=request.user,
            filename=csv_file.name,
            total_equipment=len(rows)
        )
        
        # Loop through rows and create equipment entries
        equipment_list = []
        total_flowrate = 0
        total_pressure = 0
        total_temperature = 0
        
        for row in rows:
            flowrate = float(row['Flowrate'])
            pressure = float(row['Pressure'])
            temperature = float(row['Temperature'])
            
            equipment = Equipment(
                equipment_name=row['Equipment Name'],
                type=row['Type'],
                flowrate=flowrate,
                pressure=pressure,
                temperature=temperature,
                upload_session=session
            )
            equipment_list.append(equipment)
            
            # Calculate totals for averages
            total_flowrate += flowrate
            total_pressure += pressure
            total_temperature += temperature
        
        # Bulk create for efficiency
        Equipment.objects.bulk_create(equipment_list)
        
        # Store averages
        count = len(rows)
        session.avg_flowrate = total_flowrate / count if count > 0 else 0
        session.avg_pressure = total_pressure / count if count > 0 else 0
        session.avg_temperature = total_temperature / count if count > 0 else 0
        session.save()
        
        print(f"Successfully uploaded {count} equipment entries")  # debug print
        
        return Response({
            'message': 'CSV uploaded successfully',
            'session_id': session.id,
            'total_equipment': count,
            'averages': {
                'flowrate': session.avg_flowrate,
                'pressure': session.avg_pressure,
                'temperature': session.avg_temperature
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        print(f"Error uploading CSV: {str(e)}")  # debug print
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Get summary for a session
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_summary(request, session_id):
    try:
        session = UploadSession.objects.get(id=session_id, user=request.user)
        equipments = Equipment.objects.filter(upload_session=session)
        
        # Get equipment type distribution
        type_counts = {}
        for equipment in equipments:
            if equipment.type in type_counts:
                type_counts[equipment.type] += 1
            else:
                type_counts[equipment.type] = 1
        
        return Response({
            'session_id': session.id,
            'filename': session.filename,
            'upload_date': session.upload_date,
            'total_equipment': session.total_equipment,
            'averages': {
                'flowrate': session.avg_flowrate,
                'pressure': session.avg_pressure,
                'temperature': session.avg_temperature
            },
            'type_distribution': type_counts
        })
        
    except UploadSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)


# Get equipment list for a session
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_equipment_list(request, session_id):
    try:
        session = UploadSession.objects.get(id=session_id, user=request.user)
        equipments = Equipment.objects.filter(upload_session=session)
        serializer = EquipmentSerializer(equipments, many=True)
        return Response(serializer.data)
    except UploadSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)


# Get upload history (last 5)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_history(request):
    sessions = UploadSession.objects.filter(user=request.user)[:5]  # last 5
    serializer = UploadSessionSerializer(sessions, many=True)
    return Response(serializer.data)


# Get chart data
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chart_data(request, session_id):
    try:
        session = UploadSession.objects.get(id=session_id, user=request.user)
        equipments = Equipment.objects.filter(upload_session=session)
        
        # Type distribution data
        type_counts = {}
        for equipment in equipments:
            if equipment.type in type_counts:
                type_counts[equipment.type] += 1
            else:
                type_counts[equipment.type] = 1
        
        # Equipment names and values for bar chart
        names = [eq.equipment_name for eq in equipments]
        flowrates = [eq.flowrate for eq in equipments]
        pressures = [eq.pressure for eq in equipments]
        temperatures = [eq.temperature for eq in equipments]
        
        return Response({
            'type_distribution': type_counts,
            'equipment_names': names,
            'flowrates': flowrates,
            'pressures': pressures,
            'temperatures': temperatures
        })
        
    except UploadSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)


# Generate PDF report using reportlab (student approach - actual PDF file)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_pdf(request, session_id):
    """Generate actual PDF file using reportlab"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from io import BytesIO
        
        print(f"Generating PDF for session {session_id}")  # debug
        
        session = UploadSession.objects.get(id=session_id, user=request.user)
        equipments = Equipment.objects.filter(upload_session=session)
        
        # Calculate type distribution manually (student approach)
        type_counts = {}
        for equipment in equipments:
            eq_type = equipment.type
            if eq_type in type_counts:
                type_counts[eq_type] += 1
            else:
                type_counts[eq_type] = 1
        
        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph("<b>Equipment Analysis Report</b>", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Summary section
        summary_text = f"""
        <b>File:</b> {session.filename}<br/>
        <b>Upload Date:</b> {session.upload_date.strftime('%Y-%m-%d %H:%M')}<br/>
        <b>Total Equipment:</b> {session.total_equipment}<br/>
        <b>Average Flowrate:</b> {session.avg_flowrate:.2f}<br/>
        <b>Average Pressure:</b> {session.avg_pressure:.2f}<br/>
        <b>Average Temperature:</b> {session.avg_temperature:.2f}<br/>
        """
        summary = Paragraph(summary_text, styles['Normal'])
        elements.append(summary)
        elements.append(Spacer(1, 0.3*inch))
        
        # Equipment type distribution table
        type_title = Paragraph("<b>Equipment Type Distribution</b>", styles['Heading2'])
        elements.append(type_title)
        elements.append(Spacer(1, 0.1*inch))
        
        type_data = [['Type', 'Count', 'Percentage']]
        for eq_type, count in type_counts.items():
            percentage = (count / session.total_equipment) * 100
            type_data.append([eq_type, str(count), f"{percentage:.1f}%"])
        
        type_table = Table(type_data)
        type_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(type_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Equipment details table
        details_title = Paragraph("<b>Equipment Details</b>", styles['Heading2'])
        elements.append(details_title)
        elements.append(Spacer(1, 0.1*inch))
        
        details_data = [['Name', 'Type', 'Flowrate', 'Pressure', 'Temp']]
        for equipment in equipments:
            details_data.append([
                equipment.equipment_name,
                equipment.type,
                str(equipment.flowrate),
                str(equipment.pressure),
                str(equipment.temperature)
            ])
        
        details_table = Table(details_data)
        details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8)
        ]))
        elements.append(details_table)
        
        # Build the PDF
        doc.build(elements)
        buffer.seek(0)
        
        # Return PDF as download
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="equipment_report_{session_id}.pdf"'
        
        print("PDF generated successfully!")  # debug
        return response
        
    except UploadSession.DoesNotExist:
        return Response({'error': 'Session not found'}, status=404)
    except Exception as e:
        print(f"PDF generation error: {str(e)}")  # debug
        import traceback
        traceback.print_exc()  # show full error for debugging
        return Response({'error': str(e)}, status=500)


