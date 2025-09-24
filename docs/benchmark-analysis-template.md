# AI Model Benchmark Analysis Template

## 📊 Benchmark Overview

**Test File**: `src/benchmark-test.ts`  
**Total Issues**: 27+ intentional vulnerabilities and code quality issues  
**Test Date**: [DATE]  
**Models Tested**: [LIST MODELS]

---

## 🎯 Issue Detection Scorecard

### Security Issues (15 total)

| Issue Type | Count | GPT-4 Turbo | GPT-4o | GPT-4o Mini | o1-preview | o1-mini |
|------------|-------|-------------|--------|-------------|------------|---------|
| SQL Injection | 5 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| XSS Vulnerabilities | 2 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Hardcoded Secrets | 3 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Command Injection | 2 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Crypto Weaknesses | 2 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Auth Bypass | 1 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |

### Performance Issues (5 total)

| Issue Type | Count | GPT-4 Turbo | GPT-4o | GPT-4o Mini | o1-preview | o1-mini |
|------------|-------|-------------|--------|-------------|------------|---------|
| Race Conditions | 1 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Memory Leaks | 2 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Inefficient Algorithms | 1 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Blocking Operations | 1 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |

### Code Quality Issues (7+ total)

| Issue Type | Count | GPT-4 Turbo | GPT-4o | GPT-4o Mini | o1-preview | o1-mini |
|------------|-------|-------------|--------|-------------|------------|---------|
| Type Safety | 4 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Info Disclosure | 2 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Error Handling | 1+ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |

---

## 📈 Model Performance Comparison

### Detection Rate

| Model | Security Issues Found | Performance Issues Found | Quality Issues Found | Total Score |
|-------|----------------------|-------------------------|---------------------|-------------|
| GPT-4 Turbo | __/15 (__%) | __/5 (__%) | __/7 (__%) | __/27 (__%) |
| GPT-4o | __/15 (__%) | __/5 (__%) | __/7 (__%) | __/27 (__%) |
| GPT-4o Mini | __/15 (__%) | __/5 (__%) | __/7 (__%) | __/27 (__%) |
| o1-preview | __/15 (__%) | __/5 (__%) | __/7 (__%) | __/27 (__%) |
| o1-mini | __/15 (__%) | __/5 (__%) | __/7 (__%) | __/27 (__%) |

### Solution Quality (1-5 scale)

| Model | Code Examples | Explanation Quality | Actionability | Alternative Solutions | Overall |
|-------|---------------|-------------------|---------------|---------------------|---------|
| GPT-4 Turbo | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| GPT-4o | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| GPT-4o Mini | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| o1-preview | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| o1-mini | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

### Performance Metrics

| Model | Response Time | Token Usage | Cost Efficiency | Inline Comments Quality |
|-------|--------------|-------------|----------------|------------------------|
| GPT-4 Turbo | __ seconds | __ tokens | __ | ⭐⭐⭐⭐⭐ |
| GPT-4o | __ seconds | __ tokens | __ | ⭐⭐⭐⭐⭐ |
| GPT-4o Mini | __ seconds | __ tokens | __ | ⭐⭐⭐⭐⭐ |
| o1-preview | __ seconds | __ tokens | __ | ⭐⭐⭐⭐⭐ |
| o1-mini | __ seconds | __ tokens | __ | ⭐⭐⭐⭐⭐ |

---

## 🏆 Key Findings

### Best Overall Model
**Winner**: [MODEL NAME]
- **Strengths**: [LIST KEY STRENGTHS]
- **Detection Rate**: __% 
- **Solution Quality**: ⭐⭐⭐⭐⭐

### Best for Security
**Winner**: [MODEL NAME]
- **Security Detection**: __/15 (__%)
- **Notable**: [SPECIFIC SECURITY FINDINGS]

### Best for Performance Analysis  
**Winner**: [MODEL NAME]
- **Performance Detection**: __/5 (__%)
- **Notable**: [SPECIFIC PERFORMANCE FINDINGS]

### Best Value (Cost vs Quality)
**Winner**: [MODEL NAME]
- **Cost Efficiency**: [RATING]
- **Quality Score**: __/27 (__%)

---

## 📝 Detailed Analysis Notes

### Unique Detections
- **GPT-4 Turbo**: [Issues only this model found]
- **GPT-4o**: [Issues only this model found]  
- **GPT-4o Mini**: [Issues only this model found]
- **o1-preview**: [Issues only this model found]
- **o1-mini**: [Issues only this model found]

### Missed Critical Issues
- **All Models Missed**: [Critical issues none detected]
- **Most Models Missed**: [Issues only 1-2 models found]

### False Positives
- **GPT-4 Turbo**: [Incorrect issues reported]
- **GPT-4o**: [Incorrect issues reported]
- **GPT-4o Mini**: [Incorrect issues reported]  
- **o1-preview**: [Incorrect issues reported]
- **o1-mini**: [Incorrect issues reported]

---

## 🎯 Recommendations

### For Production Use
1. **Primary Model**: [RECOMMENDED MODEL] - Best overall balance
2. **Security Focus**: [RECOMMENDED MODEL] - Best security detection
3. **Cost Optimization**: [RECOMMENDED MODEL] - Best value for money

### Model-Specific Use Cases
- **Complex Security Analysis**: Use [MODEL] for thorough security reviews
- **Performance Optimization**: Use [MODEL] for performance-critical code
- **General Code Quality**: Use [MODEL] for everyday PR reviews
- **Budget-Conscious**: Use [MODEL] for cost-effective reviews

---

## 📊 Benchmark Conclusions

### Summary
[Write overall conclusions about model performance, strengths, and trade-offs]

### Future Testing
- [ ] Test with different programming languages
- [ ] Benchmark on real-world codebases
- [ ] Test with different prompt engineering approaches
- [ ] Evaluate consistency across multiple runs