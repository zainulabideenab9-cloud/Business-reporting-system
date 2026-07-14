<div align="center">
  <h1>BUSINESS REPORTING SYSTEM</h1>
  <p><strong>Operational Tracking, Analytics, and Maintenance Framework</strong></p>
  
  <hr />
  
  <p>
    <a href="#core-features">Features</a> &bull; 
    <a href="#tech-stack">Tech Stack</a> &bull; 
    <a href="#deployment">Deployment</a> &bull; 
    <a href="#access-credentials">Access Credentials</a> &bull; 
    <a href="#troubleshooting">Troubleshooting</a>
  </p>
  
  <hr />
</div>

<h2 id="core-features">1. CORE FEATURES</h2>
<ul>
  <li>
    <strong>IDENTITY MANAGEMENT</strong><br />
    Secure authentication with distinct permission levels for Administrative and Staff roles.
  </li>
  <li>
    <strong>DATA VISUALIZATION</strong><br />
    Dynamic dashboard featuring KPI tracking and interactive analytical charts.
  </li>
  <li>
    <strong>OPERATIONAL INPUT</strong><br />
    Streamlined portals for project registration, customer logging, and budget management.
  </li>
  <li>
    <strong>ANALYTICS &amp; FORECASTING</strong><br />
    Advanced administrative tools for trend analysis and predictive insights.
  </li>
  <li>
    <strong>DOCUMENTATION ENGINE</strong><br />
    Multi-format export capabilities supporting CSV, PDF, and SQL data structures.
  </li>
  <li>
    <strong>SYSTEM MAINTENANCE</strong><br />
    Comprehensive audit trails, budget alerts, and automated data seeding tools.
  </li>
</ul>

<hr />

<h2 id="tech-stack">2. TECH STACK</h2>
<table width="100%">
  <thead>
    <tr>
      <th align="left">COMPONENT</th>
      <th align="left">TECHNOLOGY</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Language</strong></td>
      <td>Python</td>
    </tr>
    <tr>
      <td><strong>Framework</strong></td>
      <td>Streamlit</td>
    </tr>
    <tr>
      <td><strong>Database</strong></td>
      <td>MySQL</td>
    </tr>
    <tr>
      <td><strong>Data Science</strong></td>
      <td>Pandas, NumPy, Scikit-learn</td>
    </tr>
    <tr>
      <td><strong>Visuals</strong></td>
      <td>Plotly</td>
    </tr>
    <tr>
      <td><strong>PDF Engine</strong></td>
      <td>FPDF</td>
    </tr>
  </tbody>
</table>

<hr />

<h2 id="deployment">3. RUN LOCALLY</h2>
<h3>Environment Configuration</h3>
<p>Execute the following commands in PowerShell within the project directory to initialize the environment:</p>

<pre><code>$env:ABRS_MYSQL_HOST="localhost"
$env:ABRS_MYSQL_PORT="3306"
$env:ABRS_MYSQL_USER="root"
$env:ABRS_MYSQL_PASSWORD='your_mysql_password'
$env:ABRS_MYSQL_DATABASE="DB"</code></pre>

<h3>Application Launch</h3>
<pre><code>streamlit run app.py</code></pre>

<hr />

<h2 id="access-credentials">4. ACCESS CREDENTIALS</h2>
<h3>Primary Administrator</h3>
<ul>
  <li><strong>Identifier:</strong> admin@brs.local</li>
  <li><strong>Credential:</strong> admin123</li>
</ul>

<h3>Demonstration Accounts</h3>
<table width="100%">
  <thead>
    <tr>
      <th align="left">USER IDENTITY</th>
      <th align="left">STANDARD CREDENTIAL</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>ayesha@brs.local</td>
      <td>employee123</td>
    </tr>
    <tr>
      <td>hamza@brs.local</td>
      <td>employee123</td>
    </tr>
    <tr>
      <td>sara@brs.local</td>
      <td>employee123</td>
    </tr>
  </tbody>
</table>

<blockquote>
  <p><strong>Note on Data Management:</strong><br />
  Database records can be re-initialized or cleared via the <strong>Maintenance &gt; Reset Demo Data</strong> interface within the application.</p>
</blockquote>

<hr />

<h2 id="troubleshooting">5. COMMON TROUBLESHOOTING</h2>
<ul>
  <li><strong>AUTHENTICATION FAILURE:</strong> Verify that the MySQL user credentials match the environment variables provided in Step 3.</li>
  <li><strong>DATABASE SCHEMA ERROR:</strong> Ensure the target database has been created or that the <code>ABRS_MYSQL_DATABASE</code> variable points to a valid schema.</li>
  <li><strong>PORT CONFLICT:</strong> Confirm that the MySQL service is active and listening on port 3306.</li>
</ul>

<hr />

