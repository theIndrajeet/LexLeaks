# LexLeaks Netlify Deployment Guide

## ✅ Completed Steps
1. ✅ Removed old Netlify configuration files
2. ✅ Created new clean Netlify configuration in `frontend-lexleaks/netlify.toml`
3. ✅ Committed and pushed changes to GitHub

## 🚀 Next Steps - Deploy on Netlify

### 1. Create New Site on Netlify
1. Go to [app.netlify.com](https://app.netlify.com)
2. Click **"Add new site"** → **"Import an existing project"**
3. Choose **GitHub** as your Git provider
4. Authorize Netlify to access your GitHub account if needed
5. Select the **LexLeaks** repository

### 2. Configure Build Settings
When prompted, use these settings:

- **Base directory**: `frontend-lexleaks`
- **Build command**: `npm run build`
- **Publish directory**: (leave empty - the Next.js plugin will handle it)

### 3. Environment Variables
Click on **"Show advanced"** and add:

| Key | Value |
|-----|-------|
| `NEXT_PUBLIC_API_URL` | `https://lexleaks-api-563011146464.asia-south1.run.app` |

### 4. Deploy Site
Click **"Deploy site"** and wait for the build to complete (usually 2-5 minutes).

## 📋 Post-Deployment Testing

### Test Public Pages
- [ ] Visit your Netlify URL (e.g., `https://amazing-site-123.netlify.app`)
- [ ] Check homepage loads
- [ ] Check if posts are displayed (if any exist)
- [ ] Test navigation to About page
- [ ] Test navigation to Archive page
- [ ] Test navigation to Submit page

### Test Admin Functions
- [ ] Go to `/admin/login`
- [ ] Login with:
  - Username: `admin`
  - Password: `LexLeaks2024!`
- [ ] Access admin dashboard
- [ ] Try creating a test post
- [ ] Publish the test post
- [ ] Verify it appears on the public homepage

### API Connection Test
- [ ] Open browser console (F12)
- [ ] Check for any API connection errors
- [ ] Verify posts load from the Google Cloud backend

## 🌐 Custom Domain (Optional)

If you have a custom domain:

1. Go to **"Domain settings"** in your Netlify site
2. Click **"Add custom domain"**
3. Enter your domain (e.g., `lexleaks.com`)
4. Update your DNS records as instructed:
   - Add CNAME record pointing to your Netlify subdomain
   - Or use Netlify DNS for automatic configuration
5. Wait for DNS propagation (5-30 minutes)
6. Netlify will automatically provision SSL certificate

## 🔧 Troubleshooting

### If build fails:
- Check the build logs in Netlify
- Common issues:
  - Missing dependencies: Check `package.json`
  - Node version mismatch: We've set it to v18 in config
  - Build errors: Check for TypeScript or ESLint errors

### If API connection fails:
- Verify Google Cloud backend is running: `https://lexleaks-api-563011146464.asia-south1.run.app`
- Check CORS settings on backend
- Verify environment variable is set correctly in Netlify

### If posts don't appear:
- Check if there are posts in the database
- Use the admin panel to create and publish posts
- Check browser console for API errors

## 📞 Support Resources

- [Netlify Documentation](https://docs.netlify.com)
- [Next.js on Netlify Guide](https://docs.netlify.com/integrations/frameworks/next-js/)
- [Netlify Support Forum](https://answers.netlify.com/)

## 🎉 Success!
Once deployed, your LexLeaks site will be live with:
- Automatic HTTPS
- Global CDN
- Automatic deployments on git push
- Preview deployments for pull requests 