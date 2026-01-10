export function Privacy() {
  return (
    <div className="page-status" style={{ minHeight: '100vh', padding: '48px 24px', maxWidth: '900px', margin: '0 auto', textAlign: 'left' }}>
      <div style={{ background: 'white', borderRadius: '24px', padding: '48px', boxShadow: 'var(--shadow-soft)' }}>
        <h1 style={{ fontFamily: 'var(--font-display)', marginBottom: '8px' }}>Privacy Policy</h1>
        <p style={{ color: 'var(--ink-500)', marginBottom: '32px' }}>Last updated: January 10, 2026</p>

        <section style={{ marginBottom: '32px' }}>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem', marginBottom: '12px' }}>1. Introduction</h2>
          <p style={{ lineHeight: '1.6', color: 'var(--ink-700)' }}>
            Safe Drive Africa ("we", "our", or "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our DataHub application and services.
          </p>
        </section>

        <section style={{ marginBottom: '32px' }}>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem', marginBottom: '12px' }}>2. Information We Collect</h2>
          <h3 style={{ fontSize: '1.1rem', marginTop: '16px', marginBottom: '8px' }}>2.1 Driver Information</h3>
          <ul style={{ lineHeight: '1.8', color: 'var(--ink-700)' }}>
            <li>Email address and password for authentication</li>
            <li>Driver profile ID and name</li>
            <li>Driving behavior data and telematics</li>
            <li>Trip information (routes, duration, timestamps)</li>
            <li>Safety scores and performance metrics (UBPK scores)</li>
            <li>Questionnaire responses (alcohol consumption patterns)</li>
          </ul>

          <h3 style={{ fontSize: '1.1rem', marginTop: '16px', marginBottom: '8px' }}>2.2 Fleet and Organization Information</h3>
          <ul style={{ lineHeight: '1.8', color: 'var(--ink-700)' }}>
            <li>Fleet manager and administrator account details</li>
            <li>Organization and fleet configuration</li>
            <li>API keys and access credentials</li>
            <li>Insurance partner information</li>
          </ul>

          <h3 style={{ fontSize: '1.1rem', marginTop: '16px', marginBottom: '8px' }}>2.3 Technical Information</h3>
          <ul style={{ lineHeight: '1.8', color: 'var(--ink-700)' }}>
            <li>Device information and browser type</li>
            <li>IP addresses and location data</li>
            <li>Usage data and analytics</li>
            <li>Log files and error reports</li>
          </ul>
        </section>

        <section style={{ marginBottom: '32px' }}>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem', marginBottom: '12px' }}>3. How We Use Your Information</h2>
          <ul style={{ lineHeight: '1.8', color: 'var(--ink-700)' }}>
            <li><strong>Safety Analysis:</strong> To analyze driving patterns and provide safety insights</li>
            <li><strong>Performance Tracking:</strong> To calculate and display safety scores and rankings</li>
            <li><strong>Research:</strong> To conduct road safety research and improve algorithms</li>
            <li><strong>Fleet Management:</strong> To help fleet managers monitor and improve driver safety</li>
            <li><strong>Insurance Services:</strong> To provide telematics data to insurance partners</li>
            <li><strong>Communication:</strong> To send alerts, tips, and updates about your driving performance</li>
            <li><strong>Service Improvement:</strong> To enhance and optimize our platform</li>
          </ul>
        </section>

        <section style={{ marginBottom: '32px' }}>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem', marginBottom: '12px' }}>4. Data Sharing and Disclosure</h2>
          <p style={{ lineHeight: '1.6', color: 'var(--ink-700)', marginBottom: '12px' }}>
            We may share your information with:
          </p>
          <ul style={{ lineHeight: '1.8', color: 'var(--ink-700)' }}>
            <li><strong>Your Fleet Manager:</strong> If you're part of a fleet, your employer may access your driving data</li>
            <li><strong>Insurance Partners:</strong> If enrolled in an insurance telematics program</li>
            <li><strong>Researchers:</strong> Anonymized and aggregated data for road safety research</li>
            <li><strong>Service Providers:</strong> Third-party vendors who assist in operating our platform</li>
            <li><strong>Legal Requirements:</strong> When required by law or to protect rights and safety</li>
          </ul>
        </section>

        <section style={{ marginBottom: '32px' }}>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem', marginBottom: '12px' }}>5. Data Security</h2>
          <p style={{ lineHeight: '1.6', color: 'var(--ink-700)' }}>
            We implement industry-standard security measures to protect your data:
          </p>
          <ul style={{ lineHeight: '1.8', color: 'var(--ink-700)' }}>
            <li>Encryption of data in transit (HTTPS/TLS)</li>
            <li>Secure authentication using JWT tokens and API keys</li>
            <li>Regular security audits and updates</li>
            <li>Access controls and role-based permissions</li>
            <li>Secure cloud infrastructure</li>
          </ul>
        </section>

        <section style={{ marginBottom: '32px' }}>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem', marginBottom: '12px' }}>6. Your Rights</h2>
          <p style={{ lineHeight: '1.6', color: 'var(--ink-700)', marginBottom: '12px' }}>
            You have the right to:
          </p>
          <ul style={{ lineHeight: '1.8', color: 'var(--ink-700)' }}>
            <li><strong>Access:</strong> Request a copy of your personal data</li>
            <li><strong>Correction:</strong> Update or correct inaccurate information</li>
            <li><strong>Deletion:</strong> Request deletion of your data (subject to legal requirements)</li>
            <li><strong>Opt-out:</strong> Disable data sync or withdraw from the program</li>
            <li><strong>Portability:</strong> Export your data in a machine-readable format</li>
          </ul>
        </section>

        <section style={{ marginBottom: '32px' }}>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem', marginBottom: '12px' }}>7. Data Retention</h2>
          <p style={{ lineHeight: '1.6', color: 'var(--ink-700)' }}>
            We retain your data for as long as necessary to provide our services, comply with legal obligations, and for research purposes. Historical driving data may be retained in anonymized form for research and safety analysis.
          </p>
        </section>

        <section style={{ marginBottom: '32px' }}>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem', marginBottom: '12px' }}>8. Cookies and Tracking</h2>
          <p style={{ lineHeight: '1.6', color: 'var(--ink-700)' }}>
            We use local storage to maintain your login session and preferences. We do not use third-party advertising cookies.
          </p>
        </section>

        <section style={{ marginBottom: '32px' }}>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem', marginBottom: '12px' }}>9. Children's Privacy</h2>
          <p style={{ lineHeight: '1.6', color: 'var(--ink-700)' }}>
            Our services are not intended for individuals under 18 years of age. We do not knowingly collect personal information from children.
          </p>
        </section>

        <section style={{ marginBottom: '32px' }}>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem', marginBottom: '12px' }}>10. Changes to This Policy</h2>
          <p style={{ lineHeight: '1.6', color: 'var(--ink-700)' }}>
            We may update this Privacy Policy from time to time. We will notify you of significant changes by posting the new policy on this page and updating the "Last updated" date.
          </p>
        </section>

        <section style={{ marginBottom: '32px' }}>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem', marginBottom: '12px' }}>11. Contact Us</h2>
          <p style={{ lineHeight: '1.6', color: 'var(--ink-700)' }}>
            If you have questions about this Privacy Policy or wish to exercise your rights, please contact us at:
          </p>
          <p style={{ lineHeight: '1.6', color: 'var(--ink-700)', marginTop: '12px' }}>
            <strong>Safe Drive Africa</strong><br />
            Email: privacy@safedriveafrica.com<br />
            Website: https://safedriveafrica.com
          </p>
        </section>

        <div style={{ marginTop: '48px', paddingTop: '24px', borderTop: '1px solid rgba(18, 32, 24, 0.08)', textAlign: 'center' }}>
          <a href="/login" style={{ color: 'var(--sage-700)', textDecoration: 'none', fontWeight: 600 }}>
            ← Back to Login
          </a>
        </div>
      </div>
    </div>
  )
}
