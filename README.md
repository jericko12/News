
📰 News Explorer App

A modern Python desktop application for exploring, reading, and sharing news articles from around the world. Built with Tkinter and powered by NewsAPI.

![News API](https://newsapi.org/images/n-logo-border.png)

🌟 Features

- 🔍 Search news articles from over 150,000 sources
- 📱 Modern card and list view layouts
- 📂 Save articles for offline reading
- 🔄 Real-time news updates
- 📊 Category filtering (Business, Tech, Sports, etc.)
- 📤 Easy sharing functionality
- 💾 Article bookmarking system
- 🎨 Clean and intuitive user interface

🚀 Getting Started

Prerequisites:
- Python 3.x
- NewsAPI Key (Get it from [NewsAPI](https://newsapi.org/register))

Installation:

1. Clone the repository:
```bash
git clone https://github.com/jericko12/News.git
cd news-explorer
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a config.py file with your API key:
```python
API_KEY = 'your_api_key_here'
```

4. Run the application:
```bash
python news_app.py
```

📋 Usage

Search Articles:
- Use the search bar to find articles by keyword
- Filter results by category using the toolbar buttons
- Toggle between list and card views

Save Articles:
- Click the "⭐ Save" button to save articles for offline reading
- Access saved articles in the "📂 Saved" tab
- Articles are stored in your Documents folder

Share Articles:
- Use the "🔗 Share" button to copy article URLs
- Open articles directly in your browser
- Quick copy-paste functionality for sharing

🔑 API Documentation

This app uses NewsAPI for fetching news articles. Key endpoints:

Everything Endpoint:
```
GET https://newsapi.org/v2/everything
```
Search through millions of articles from over 50,000 large and small news sources and blogs.

Top Headlines:
```
GET https://newsapi.org/v2/top-headlines
```
Get breaking news headlines, and search news articles published by over 50,000 sources.

For more details, visit the [NewsAPI Documentation](https://newsapi.org/docs/get-started).

🛠️ Advanced Features

Keyboard Shortcuts:
- Ctrl + F: Focus search bar
- Ctrl + R: Refresh headlines
- Ctrl + Left/Right: Navigate pages
- Ctrl + L: Clear search

View Modes:
- List View: Compact view for quick scanning
- Card View: Rich visual presentation with images

Article Management:
- Save for offline reading
- Organize by categories
- Search within saved articles
- Export as text files

Customization:
- Adjustable font sizes
- Theme customization
- Layout preferences
- Category filters

🔧 Technical Details

Dependencies:
```
newsapi-python==0.2.6
tkinter
Pillow==9.0.0
requests==2.27.1
ttkthemes==3.2.2
```

File Structure:
```
news-explorer/
│
├── news_app.py          # Main application file
├── config.py           # API configuration
├── requirements.txt    # Project dependencies
├── README.md          # Documentation
│
├── assets/            # Application assets
│   ├── icons/        # UI icons
│   └── themes/       # Theme files
│
└── docs/             # Additional documentation
```

💡 Tips and Tricks

Optimizing Searches:
- Use specific keywords
- Filter by date range
- Combine category filters
- Use quotation marks for exact phrases

Managing Saved Articles:
- Search within saved articles
- Right-click for options
- Open containing folder
- Regular refresh

🔄 Updates and Maintenance

Version History:
- v1.0.0: Initial release
- v1.1.0: Added card view
- v1.2.0: Implemented saving feature
- v1.3.0: Added search suggestions

Planned Features:
- Dark mode support
- Custom categories
- Article analytics
- Export to PDF
- Multiple language support

🐛 Troubleshooting

Common Issues:
1. API Key Issues
   - Verify key in config.py
   - Check API rate limits
   - Ensure internet connectivity

2. Display Problems
   - Update tkinter
   - Check screen resolution
   - Verify theme compatibility

3. Saving Errors
   - Check write permissions
   - Verify storage space
   - Update file path settings

📊 API Usage Guidelines

Rate Limits:
- Developer Plan: 100 requests/day
- Business Plan: 50,000 requests/month
- Enterprise Plan: Custom limits

Best Practices:
- Cache responses when appropriate
- Implement error handling
- Use appropriate endpoints
- Monitor API usage

🔐 Security

Data Privacy:
- No personal data collection
- Local storage only
- Secure API key handling

Best Practices:
- Never share API keys
- Update dependencies regularly
- Use secure connections

🌐 Community and Support

Contributing:
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

Support Channels:
- GitHub Issues
- Email Support
- Community Forums

📈 Future Development

Roadmap:
1. Q1 2024: Dark mode, optimizations
2. Q2 2024: AI suggestions, social integration
3. Q3 2024: Mobile app, browser extension

💖 Support the Project

If you find this project helpful:
- Star the repository
- Report issues
- Contribute code
- Share with others
- Make a donation

Made with ❤️ by Jericko
Contact: [@justcallme.eko](https://www.instagram.com/justcallme.eko/)
Project Link: [https://github.com/jericko12/News](https://github.com/jericko12/News)