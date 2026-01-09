# Fixing 404 Errors on Page Refresh (SPA Routing)

## Problem
When you refresh a page like `/driver/trips` or `/admin/api-clients`, you get a 404 error. This happens because Apache tries to find that file on disk instead of serving `index.html` for React Router to handle.

## Solution

You've already cleared the proxy directives that were forwarding to the old FastAPI backend. Now you need to ensure Apache properly handles SPA routing.

### Option 1: Using Plesk Apache & nginx Settings (Recommended)

1. **Go to Plesk**: Domains → datahub.safedriveafrica.com → **Apache & nginx Settings**

2. **In the "Additional directives for HTTP" field**, add:
```apache
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
  RewriteRule ^index\.html$ - [L]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteCond %{REQUEST_FILENAME} !-l
  RewriteRule . /index.html [L]
</IfModule>
```

3. **In the "Additional directives for HTTPS" field**, add the same:
```apache
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
  RewriteRule ^index\.html$ - [L]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteCond %{REQUEST_FILENAME} !-l
  RewriteRule . /index.html [L]
</IfModule>
```

4. Click **OK** or **Apply**

### Option 2: Using File Manager (If Apache directives don't work)

If the Apache directives don't work, you can create/edit the `.htaccess` file:

1. **Go to Plesk File Manager**
2. Navigate to `/var/www/vhosts/safedriveafrica.com/datahub.safedriveafrica.com/`
3. Check if `.htaccess` file exists (you may need to show hidden files)
4. If it exists, edit it. If not, create it with this content:

```apache
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
  RewriteRule ^index\.html$ - [L]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteCond %{REQUEST_FILENAME} !-l
  RewriteRule . /index.html [L]
</IfModule>

# Security headers
<IfModule mod_headers.c>
  Header set X-Frame-Options "SAMEORIGIN"
  Header set X-Content-Type-Options "nosniff"
  Header set X-XSS-Protection "1; mode=block"
  Header set Referrer-Policy "strict-origin-when-cross-origin"
</IfModule>

# Compression
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css text/javascript application/javascript application/json
</IfModule>

# Cache static assets
<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType image/jpg "access plus 1 year"
  ExpiresByType image/jpeg "access plus 1 year"
  ExpiresByType image/gif "access plus 1 year"
  ExpiresByType image/png "access plus 1 year"
  ExpiresByType image/svg+xml "access plus 1 year"
  ExpiresByType text/css "access plus 1 year"
  ExpiresByType application/javascript "access plus 1 year"
  ExpiresByType font/woff "access plus 1 year"
  ExpiresByType font/woff2 "access plus 1 year"
</IfModule>
```

## What This Does

- **RewriteEngine On**: Enables URL rewriting
- **RewriteCond %{REQUEST_FILENAME} !-f**: Check if the request is NOT for an existing file
- **RewriteCond %{REQUEST_FILENAME} !-d**: Check if the request is NOT for an existing directory
- **RewriteCond %{REQUEST_FILENAME} !-l**: Check if the request is NOT for a symbolic link
- **RewriteRule . /index.html [L]**: If none of the above, serve index.html (let React Router handle it)

## Testing

After applying the fix:

1. Visit https://datahub.safedriveafrica.com/driver/trips
2. Refresh the page (F5 or Ctrl+R)
3. You should see the page load correctly, not a 404

## Troubleshooting

If you still get 404 errors:

1. **Check if mod_rewrite is enabled**:
   - In Plesk, go to **Tools & Settings** → **Apache Web Server** → Check if `mod_rewrite` is enabled

2. **Check Apache error logs** in Plesk:
   - Domains → datahub.safedriveafrica.com → **Logs** → **Error Log**

3. **Verify .htaccess is being read**:
   - Add a syntax error to `.htaccess` and see if Apache throws an error
   - If no error, Apache might be ignoring .htaccess files

4. **Contact IONOS support** if mod_rewrite is disabled or .htaccess files are not allowed
