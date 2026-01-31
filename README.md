# Amazon Store Brands Scraper

Efficiently scrape product information from Amazon store brands with customizable data extraction. Perfect for market research, competitive analysis, and product monitoring.

## Features

- 🎯 **Multi-brand scraping** - Extract data from multiple Amazon store brands in a single run
- 🔧 **Flexible data selection** - Choose exactly which product fields to scrape (ASIN, page URL, image URL)
- 🚀 **Scalable** - Set limits on products per brand or scrape entire catalogs
- 🛡️ **Reliable** - Built-in retry logic and proxy support to handle Amazon's anti-scraping measures
- 📊 **Organized output** - Results grouped by brand or flattened for easy analysis

## Input Configuration

### Basic Setup

The scraper requires at least one brand configuration. For each brand, specify:

- **Brand Name** (required): The exact Amazon store brand name
- **Data Fields**: Choose which information to collect:
  - ASIN (Amazon Standard Identification Number)
  - Product page URL
  - Product image URL

### Example Input

```json
{
  "brands": [
    {
      "brandName": "AmazonBasics",
      "scrapeAsin": true,
      "scrapePage": true,
      "scrapeImageUrl": true
    },
    {
      "brandName": "Anker",
      "scrapeAsin": true,
      "scrapePage": false,
      "scrapeImageUrl": true
    }
  ],
  "maxProductsPerBrand": 100,
  "proxyConfiguration": {
    "useApifyProxy": true,
    "apifyProxyGroups": ["RESIDENTIAL"]
  }
}
```

### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `brands` | Array | Yes | List of brand configurations with data field selections |
| `maxProductsPerBrand` | Integer | No | Limit products scraped per brand (1-10,000) |
| `proxyConfiguration` | Object | No | Proxy settings (Apify Proxy recommended) |
| `debugMode` | Boolean | No | Enable detailed logging (default: false) |
| `maxRetries` | Integer | No | Retry attempts for failed requests (default: 3) |
| `requestTimeout` | Integer | No | Page load timeout in seconds (default: 30) |
| `outputFormat` | String | No | "grouped" (by brand) or "flat" (default: grouped) |

## Output Format

### Grouped Output (Default)

Results are organized by brand name:

```json
{
  "AmazonBasics": [
    {
      "name": "USB Cable 6ft",
      "asin": "B01234ABCD",
      "page": "https://www.amazon.com/dp/B01234ABCD",
      "image_url": "https://m.media-amazon.com/images/I/example.jpg"
    },
    {
      "name": "HDMI Cable 10ft",
      "asin": "B56789EFGH",
      "page": "https://www.amazon.com/dp/B56789EFGH",
      "image_url": "https://m.media-amazon.com/images/I/example2.jpg"
    }
  ],
  "Anker": [
    {
      "name": "PowerCore 20000",
      "asin": "B09876IJKL",
      "image_url": "https://m.media-amazon.com/images/I/example3.jpg"
    }
  ]
}
```

### Flat Output

All products in a single list:

```json
[
  {
    "brand": "AmazonBasics",
    "name": "USB Cable 6ft",
    "asin": "B01234ABCD",
    "page": "https://www.amazon.com/dp/B01234ABCD",
    "image_url": "https://m.media-amazon.com/images/I/example.jpg"
  },
  {
    "brand": "AmazonBasics",
    "name": "HDMI Cable 10ft",
    "asin": "B56789EFGH",
    "page": "https://www.amazon.com/dp/B56789EFGH",
    "image_url": "https://m.media-amazon.com/images/I/example2.jpg"
  }
]
```

## Best Practices

### Proxy Configuration

Amazon actively blocks scrapers. **Always use proxies**, preferably residential:

```json
{
  "proxyConfiguration": {
    "useApifyProxy": true,
    "apifyProxyGroups": ["RESIDENTIAL"]
  }
}
```

### Rate Limiting

- Start with smaller product limits per brand
- Use appropriate request timeouts (30-60 seconds recommended)
- Enable retries to handle temporary failures

### Brand Names

- Use exact brand names as they appear on Amazon
- Brand names are case-sensitive
- Verify brand names before large scraping runs

## Common Use Cases

### Market Research
Analyze product offerings across competing brands:
```json
{
  "brands": [
    {"brandName": "Nike", "scrapeAsin": true, "scrapePage": true},
    {"brandName": "Adidas", "scrapeAsin": true, "scrapePage": true},
    {"brandName": "Puma", "scrapeAsin": true, "scrapePage": true}
  ],
  "maxProductsPerBrand": 500
}
```

### Image Collection
Gather product images for catalog building:
```json
{
  "brands": [
    {"brandName": "Samsung", "scrapeImageUrl": true, "scrapeAsin": true}
  ],
  "outputFormat": "flat"
}
```

### Product Monitoring
Track specific brand catalogs:
```json
{
  "brands": [
    {"brandName": "YourBrand", "scrapeAsin": true, "scrapePage": true, "scrapeImageUrl": true}
  ],
  "debugMode": true
}
```

## Limitations

- Requires valid Amazon brand names
- Subject to Amazon's terms of service and robots.txt
- Scraping speed depends on proxy quality and Amazon's rate limits
- Some product information may be unavailable depending on Amazon's page structure

## Troubleshooting

### No Results Returned

- Verify brand name spelling and capitalization
- Check if brand has products on Amazon
- Enable `debugMode` to see detailed logs
- Ensure proxy configuration is correct

### Frequent Failures

- Increase `requestTimeout` (try 60+ seconds)
- Use residential proxies instead of datacenter
- Reduce `maxProductsPerBrand` to avoid rate limits
- Increase `maxRetries` for unstable connections

### Missing Data Fields

- Verify the product page structure hasn't changed
- Check if specific fields are available for the brand
- Enable `debugMode` to inspect scraping process

## Support

For issues, feature requests, or questions:
- Open an issue on the Actor's page
- Check Apify documentation for general scraping help
- Review Amazon's terms of service for compliance

## Compliance

This Actor is provided for legitimate use cases such as:
- Market research with publicly available data
- Competitive analysis
- Academic research

Users are responsible for:
- Complying with Amazon's Terms of Service
- Respecting robots.txt directives
- Following applicable laws and regulations
- Using scraped data ethically and legally

---

**Note**: This Actor scrapes publicly available information from Amazon. Always ensure your use case complies with Amazon's terms of service and applicable laws.