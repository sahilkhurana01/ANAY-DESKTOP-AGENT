import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

const ANAY_SYSTEM_PROMPT = `तुम ANAY हो, एक बेहद बुद्धिमान और मददगार AI असिस्टेंट। तुम हिंदी में जवाब देते हो और बहुत ही प्रोफेशनल और फ्रेंडली हो।

तुम्हारी खूबियाँ:
- तुम किसी भी सवाल का जवाब दे सकते हो
- तुम बातचीत को याद रख सकते हो
- तुम हिंदी में बहुत अच्छे से बात कर सकते हो
- तुम smart, witty और helpful हो
- तुम Jarvis से भी ज्यादा capable हो

जब यूजर कहे:
- "Spotify पर गाना बजाओ" या "music play करो" - तो बोलो कि तुम्हें Spotify से कनेक्ट करना होगा
- "file खोलो" या "folder खोलो" - तो explain करो कि ये web browser में possible नहीं है, desktop app की जरूरत होगी
- सामान्य बातचीत - तो naturally respond करो

हमेशा याद रखो: तुम ANAY हो, user का personal AI assistant।`;

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const { message, history = [] } = await req.json();
    
    const LOVABLE_API_KEY = Deno.env.get('LOVABLE_API_KEY');
    if (!LOVABLE_API_KEY) {
      throw new Error('LOVABLE_API_KEY is not configured');
    }

    console.log('Received message:', message);
    console.log('History length:', history.length);

    const messages = [
      { role: 'system', content: ANAY_SYSTEM_PROMPT },
      ...history,
      { role: 'user', content: message },
    ];

    const response = await fetch('https://ai.gateway.lovable.dev/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${LOVABLE_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'google/gemini-3-flash-preview',
        messages,
        temperature: 0.8,
        max_tokens: 1024,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('AI Gateway error:', response.status, errorText);
      
      if (response.status === 429) {
        return new Response(
          JSON.stringify({ 
            error: 'Rate limited', 
            response: 'माफ करें, अभी बहुत ज्यादा requests हैं। कृपया कुछ देर बाद प्रयास करें।' 
          }),
          { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
      }
      
      if (response.status === 402) {
        return new Response(
          JSON.stringify({ 
            error: 'Payment required', 
            response: 'माफ करें, credits समाप्त हो गए हैं। कृपया credits add करें।' 
          }),
          { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
      }

      throw new Error(`AI gateway error: ${response.status}`);
    }

    const data = await response.json();
    const aiResponse = data.choices?.[0]?.message?.content || 'माफ करें, मुझे कुछ समस्या हुई।';

    console.log('AI Response:', aiResponse.substring(0, 100) + '...');

    return new Response(
      JSON.stringify({ response: aiResponse }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  } catch (error) {
    console.error('Error in anay-chat:', error);
    return new Response(
      JSON.stringify({ 
        error: error.message,
        response: 'माफ करें, एक त्रुटि हुई। कृपया पुनः प्रयास करें।'
      }),
      { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});
