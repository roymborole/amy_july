const MacroeconomicAnalysis = {
    getMacroeconomicAnalysis: async function(ticker, analysisId) {
        try {
            const response = await fetch('/api/macroeconomic-analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ ticker, analysis_id: analysisId }),
            });
            
            if (!response.ok) {
                throw new Error('Failed to get macroeconomic analysis');
            }
            
            const data = await response.json();
            return data.analysis;
        } catch (error) {
            console.error('Error:', error);
            throw error;
        }
    },
    
    displayAnalysis: function(analysis) {
        document.getElementById('analysis-result').innerHTML = analysis;
    }
};

export default MacroeconomicAnalysis;