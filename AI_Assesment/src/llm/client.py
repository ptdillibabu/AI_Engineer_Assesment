"""LLM client abstraction."""

import os
from typing import Optional, Callable

try:
    from openai import OpenAI, AzureOpenAI
except ImportError:
    OpenAI = None
    AzureOpenAI = None

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    from azure.identity import ClientSecretCredential
except ImportError:
    ClientSecretCredential = None


def get_azure_bearer_token_provider(
    tenant_id: str,
    client_id: str,
    client_secret: str,
    scope: str = "c626bd72-9ef7-4efe-9176-5c75800f7670/.default"
) -> Callable[[], str]:
    """Create a bearer token provider for Azure AD authentication."""
    if ClientSecretCredential is None:
        raise ImportError("azure-identity package not installed. Run: pip install azure-identity")
    
    credential = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret
    )
    
    def token_provider() -> str:
        token = credential.get_token(scope)
        return token.token
    
    return token_provider


class LLMClient:
    """Unified LLM client supporting OpenAI, Azure OpenAI, Anthropic, and Google Gemini."""
    
    def __init__(
        self,
        provider: str = "openai",
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        api_key: Optional[str] = None,
        # Azure OpenAI specific parameters
        azure_endpoint: Optional[str] = None,
        azure_api_version: Optional[str] = None,
        azure_tenant_id: Optional[str] = None,
        azure_client_id: Optional[str] = None,
        azure_client_secret: Optional[str] = None,
        azure_scope: Optional[str] = None,
    ):
        self.provider = provider.lower()
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        if self.provider == "openai":
            if OpenAI is None:
                raise ImportError("openai package not installed. Run: pip install openai")
            self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
            
        elif self.provider == "azure_openai":
            if AzureOpenAI is None:
                raise ImportError("openai package not installed. Run: pip install openai")
            
            # Get Azure configuration from parameters or environment
            endpoint = azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT", "https://azapimqa.worldbank.org/conversationalai/v2")
            api_version = azure_api_version or os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
            tenant_id = azure_tenant_id or os.getenv("AZURE_TENANT_ID")
            client_id = azure_client_id or os.getenv("AZURE_CLIENT_ID")
            client_secret = azure_client_secret or os.getenv("AZURE_CLIENT_SECRET")
            scope = azure_scope or os.getenv("AZURE_SCOPE", "https://cognitiveservices.azure.com/.default")
            
            # Validate required Azure credentials
            if not all([tenant_id, client_id, client_secret]):
                raise ValueError(
                    "Azure OpenAI requires tenant_id, client_id, and client_secret. "
                    "Set them via parameters or environment variables: "
                    "AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET"
                )
            
            # Create token provider
            token_provider = get_azure_bearer_token_provider(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret,
                scope=scope,
            )
            
            self.client = AzureOpenAI(
                azure_endpoint=endpoint,
                api_version=api_version,
                azure_ad_token_provider=token_provider,
            )
            
        elif self.provider == "anthropic":
            if anthropic is None:
                raise ImportError("anthropic package not installed. Run: pip install anthropic")
            self.client = anthropic.Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
            
        elif self.provider == "gemini":
            if genai is None:
                raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
            api_key = api_key or os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not set. Please provide an API key.")
            genai.configure(api_key=api_key)
            self.client = None  # Gemini doesn't need a client object
        else:
            raise ValueError(f"Unsupported provider: {provider}. Supported: openai, azure_openai, anthropic, gemini")
    
    def chat(
        self,
        system_prompt: str,
        messages: list[dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Send a chat request and return the response text."""
        
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens
        
        if self.provider == "openai":
            return self._chat_openai(system_prompt, messages, temp, tokens)
        elif self.provider == "azure_openai":
            return self._chat_azure_openai(system_prompt, messages, temp, tokens)
        elif self.provider == "anthropic":
            return self._chat_anthropic(system_prompt, messages, temp, tokens)
        elif self.provider == "gemini":
            return self._chat_gemini(system_prompt, messages, temp, tokens)
    
    def _chat_openai(
        self,
        system_prompt: str,
        messages: list[dict],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """OpenAI chat completion."""
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=full_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        return response.choices[0].message.content
    
    def _chat_azure_openai(
        self,
        system_prompt: str,
        messages: list[dict],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Azure OpenAI chat completion."""
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        
        response = self.client.chat.completions.create(
            model=self.model,  # This is the deployment name in Azure
            messages=full_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        return response.choices[0].message.content
    
    def _chat_anthropic(
        self,
        system_prompt: str,
        messages: list[dict],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Anthropic chat completion."""
        response = self.client.messages.create(
            model=self.model,
            system=system_prompt,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        return response.content[0].text
    
    def _chat_gemini(
        self,
        system_prompt: str,
        messages: list[dict],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Google Gemini chat completion."""
        # Build conversation with system prompt
        full_prompt = f"{system_prompt}\n\n"
        
        # Add message history
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            full_prompt += f"{role}: {msg['content']}\n\n"
        
        # Create model and generate response
        model = genai.GenerativeModel(self.model)
        
        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            ),
        )
        
        return response.text