from flask import Flask, request, render_template, redirect, url_for, flash
import pandas as pd
import os
import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend for rendering to files
import matplotlib.pyplot as plt
import io
import base64
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Necessary for flashing messages

@app.route('/')
def upload_file():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file_post():
    file_path = request.form.get('file_path')
    if not file_path or not os.path.exists(file_path):
        flash('Invalid file path, please provide a valid CSV file path.', 'error')
        return redirect(url_for('upload_file'))
    if file_path.endswith('.csv'):
        return redirect(url_for('analyze_file', file_path=file_path))
    flash('Invalid file type, please provide a CSV file.', 'error')
    return redirect(url_for('upload_file'))

@app.route('/analyze')
def analyze_file():
    file_path = request.args.get('file_path')
    df = pd.read_csv(file_path)
    
    if 'status' not in df.columns:
        return render_template('error.html', message="CSV file must contain a 'status' column.")
    
    # Extract filename
    file_name = os.path.basename(file_path)
    attack_types = df['status'].unique()
    
    
    # Assuming data processing here...
    total_count = len(df)
    attack_count = len(df[df['status'] == 'attack'])
    normal_count = total_count - attack_count
    attack_ratio = attack_count / total_count
    normal_ratio = normal_count / total_count
    
    analysis = df.describe().to_html()
    X = df.drop(columns=['status'])
    y = df['status'].apply(lambda x: 1 if x == 'attack' else 0)
    X = pd.get_dummies(X)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    # Bar chart
    buf1 = io.BytesIO()
    plt.figure()
    plt.bar(['Attack', 'Normal'], [attack_count, normal_count], color=['red', 'green'])
    plt.title('Count of Attacked vs Normal Data')
    plt.ylabel('Count')
    plt.savefig(buf1, format='png')
    buf1.seek(0)
    image_base64 = base64.b64encode(buf1.read()).decode('utf-8')
    buf1.close()
    
    # Pie chart
    buf2 = io.BytesIO()
    plt.figure()
    plt.pie([attack_count, normal_count], labels=['Attack', 'Normal'], colors=['red', 'green'], autopct='%1.1f%%')
    plt.title('Percentage of Attacked vs Normal Data')
    plt.savefig(buf2, format='png')
    buf2.seek(0)
    pie_image_base64 = base64.b64encode(buf2.read()).decode('utf-8')
    buf2.close()
    
    return render_template('analysis.html', 
                           file_name=file_name, 
                           analysis=analysis, 
                           attack_ratio=attack_ratio, 
                           normal_ratio=normal_ratio, 
                           image_base64=image_base64,
                           pie_image_base64=pie_image_base64,
                           accuracy=accuracy,)

if __name__ == '__main__':
    app.run(debug=True)