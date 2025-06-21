# Azure OpenAI Migration Guide

This guide documents the migration from standard OpenAI to Azure OpenAI for the ACME Cultural Funding Analysis project.

## Overview

The system has been updated to use Azure OpenAI as the primary LLM provider while maintaining backward compatibility with standard OpenAI. This ensures better security, compliance, and enterprise-grade support.

## Key Changes

### 1. Configuration Updates

**New Environment Variables:**
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI resource endpoint
- `AZURE_OPENAI_API_KEY`: Your Azure API key
- `AZURE_OPENAI_DEPLOYMENT_NAME`: The deployment name for your GPT-4.1 model
- `AZURE_OPENAI_API_VERSION`: API version (default: 2024-02-15-preview)

### 2. Client Architecture

The `LLMClient` class now:
- Automatically detects Azure OpenAI credentials
- Falls back to standard OpenAI if Azure is not configured
- Provides a unified interface for both providers

### 3. Updated Files

- `src/config.py`: Added Azure OpenAI configuration fields
- `src/llm/client.py`: Updated to use AzureOpenAI client
- `src/features/extractor.py`: Migrated to use LLMClient
- `src/features/analyzer.py`: Migrated to use LLMClient
- `src/features/synthesizer.py`: Migrated to use LLMClient
- `src/features/program_analyzer.py`: Migrated to use LLMClient
- `.env.example`: Added Azure OpenAI configuration template

## Migration Steps

1. **Update Environment Variables**
   ```bash
   # Edit .env file
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_API_KEY=your-api-key
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-deployment
   ```

2. **Test Connection**
   ```bash
   poetry run python test_azure_openai.py
   ```

3. **Run Analysis**
   ```bash
   # Clear cache if needed to use new provider
   rm -rf data/llm_cache/
   
   # Run analysis as usual
   poetry run python run_deep_analysis.py
   ```

## Important Notes

### API Differences

The Azure OpenAI API is compatible with the standard OpenAI API, but:
- Uses deployment names instead of model names
- Requires an endpoint URL
- May have different rate limits
- Supports enterprise features like private endpoints

### Caching

The caching system remains unchanged. Cached responses from standard OpenAI will still be used. To force re-analysis with Azure OpenAI, clear the cache:
```bash
rm -rf data/llm_cache/
rm -rf data/features/
```

### Cost Considerations

Azure OpenAI pricing may differ from standard OpenAI. Monitor your usage through the Azure portal.

## Troubleshooting

### Connection Issues

If you see connection errors:
1. Verify your endpoint URL includes `https://` and ends with `/`
2. Check your API key is correct
3. Ensure your deployment name matches exactly
4. Verify the API version is supported

### Authentication Errors

Common causes:
- Incorrect API key
- API key not authorized for the deployment
- Network restrictions (check firewall/proxy settings)

### Model Not Found

If you get "deployment not found" errors:
- Verify the deployment name in Azure portal
- Ensure the deployment is active
- Check you're using the correct resource

## Rollback Instructions

To rollback to standard OpenAI:
1. Comment out Azure variables in `.env`
2. Uncomment and set `OPENAI_API_KEY`
3. The system will automatically use standard OpenAI

## Support

For Azure OpenAI specific issues:
- Check Azure OpenAI documentation
- Review deployment settings in Azure portal
- Monitor API usage and quotas

For application issues:
- Check `data/audit/` logs
- Run `test_azure_openai.py` for diagnostics
- Review error messages for specific guidance