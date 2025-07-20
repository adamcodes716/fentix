# FenixAI Dashboard Guide

## Overview

The FenixAI Dashboard is a comprehensive web interface that provides real-time monitoring, trading controls, and system management for your AI-powered cryptocurrency trading system. This guide covers every feature, button, and functionality in detail.

## 🌐 Accessing the Dashboard

**URL**: `http://localhost:8020/dashboard`

The dashboard automatically refreshes every 10 seconds to provide real-time updates on system status, trading performance, and market conditions.

## 📱 Dashboard Layout

The dashboard is organized into several key sections:

```
┌─────────────────────────────────────────────────────────────┐
│                    🚀 FenixAI Trading System                │
├─────────────────────────────────────────────────────────────┤
│  💡 System Health  │  📊 Trading Status  │  🤖 AI Models    │
├─────────────────────────────────────────────────────────────┤
│                    🎮 Trading Controls                      │
├─────────────────────────────────────────────────────────────┤
│                    📈 System Metrics                        │
├─────────────────────────────────────────────────────────────┤
│                    🔧 System Tools                          │
└─────────────────────────────────────────────────────────────┘
```

## 🔍 Detailed Section Breakdown

### 1. System Health Panel

Located at the top-left of the dashboard, this panel shows the overall health of your trading system.

#### Status Indicators:
- **🟢 Healthy**: All systems operational
- **🟡 Degraded**: Some services have issues but system is functional
- **🔴 Unhealthy**: Critical issues require attention

#### What Each Status Means:

| Status | Color | Description | Action Required |
|--------|-------|-------------|----------------|
| **Healthy** | Green | All services running perfectly | None - system ready for trading |
| **Degraded** | Yellow | Some non-critical services down | Monitor logs, consider restart |
| **Unhealthy** | Red | Critical services unavailable | Check configuration, restart system |

#### Service Components:
- **Config Service**: Configuration loading and management
- **Ollama Service**: AI model connectivity and availability
- **Redis Service**: Data caching and session storage
- **Trading Engine**: Core trading logic and execution

### 2. Trading Status Panel

Shows current trading activity and performance metrics.

#### Key Metrics:
- **Status**: Current trading state (Active/Inactive/Paused)
- **Mode**: Trading mode (Paper/Live/Demo)
- **Uptime**: How long the system has been running
- **Trades Today**: Number of trades executed in current session
- **Performance**: Win rate and total return percentage

#### Trading States Explained:

| State | Description | What It Means |
|-------|-------------|---------------|
| **Active** | System is actively analyzing markets and placing trades | Ready to execute trades based on AI signals |
| **Inactive** | System is running but not trading | Monitoring markets but not placing orders |
| **Paused** | Trading temporarily suspended | Manual pause or automatic safety pause |
| **Demo** | Running demonstration/simulation | Not using real funds, for testing only |

### 3. AI Models Panel

Displays information about available AI models and their status.

#### Model Information:
- **Available Models**: Total count of AI models loaded
- **Model List**: Names of specific models (e.g., "qwen2.5:7b", "llama3.2:latest")
- **Status**: Whether models are responding and functional

#### Model Types:
- **Language Models**: For market analysis and decision making
- **Vision Models**: For chart pattern recognition
- **Specialized Models**: For sentiment analysis and risk assessment

### 4. Trading Controls Section

This is where you can start different types of trading sessions.

#### 🎮 Control Buttons Detailed:

##### **Start Paper Trading**
- **Purpose**: Begin basic paper trading simulation
- **Risk**: No real money involved
- **Features**: Basic market simulation, simple order tracking
- **When to Use**: Testing basic functionality, learning the system
- **Response**: Returns simulation results and trade history

##### **Start Advanced Paper Trading** 
- **Purpose**: Full-featured paper trading with AI agents
- **Risk**: No real money involved
- **Features**: Complete AI analysis, consensus decision making, advanced metrics
- **When to Use**: Testing complete system before live trading
- **Response**: Comprehensive analysis with AI reasoning and trade justification

##### **Run Demo Trading**
- **Purpose**: Execute a complete trading cycle demonstration
- **Risk**: No real money involved
- **Features**: Live market data, full AI analysis, detailed reporting
- **When to Use**: Showcasing system capabilities, training, validation
- **Response**: Detailed market analysis for multiple symbols (BTC, ETH)

##### **Start Paper Session**
- **Purpose**: Launch extended paper trading session
- **Parameters**: 
  - **Balance**: Starting virtual balance (default: $10,000)
  - **Duration**: Session length in minutes (default: 30)
  - **Symbols**: Cryptocurrency pairs to trade (default: "BTCUSDT,ETHUSDT")
- **Risk**: No real money involved
- **When to Use**: Extended testing periods, strategy validation

#### Button Response Examples:

**Paper Trading Response:**
```json
{
  "status": "success",
  "message": "Paper trading started",
  "session_id": "paper-20250720-123456",
  "balance": 10000.0,
  "mode": "simulation"
}
```

**Advanced Paper Trading Response:**
```json
{
  "status": "partial",
  "message": "Advanced paper trading partially available",
  "features": ["Basic order simulation", "Market data simulation", "Trade memory"],
  "limitations": ["Some AI agents may be unavailable"],
  "initial_balance": 10000.0
}
```

### 5. System Metrics Section

Provides real-time system performance data.

#### Performance Metrics:
- **CPU Usage**: Current processor utilization
- **Memory Usage**: RAM consumption and availability
- **Disk Usage**: Storage space utilization
- **Network Activity**: API calls and data transfer rates

#### Trading Metrics:
- **Active Positions**: Currently open trades
- **Daily P&L**: Profit and loss for current day
- **Success Rate**: Percentage of profitable trades
- **Risk Exposure**: Current risk level based on position sizes

### 6. System Tools Section

Advanced utilities for system management and monitoring.

#### 🔧 Available Tools:

##### **View System Banner**
- **Purpose**: Display ASCII art banner and system information
- **Use Case**: Branding, version information, system identification
- **Response**: Formatted text banner with FenixAI branding

##### **Check Models**
- **Purpose**: Verify AI model availability and compatibility
- **Use Case**: Troubleshooting AI connectivity, model validation
- **Response**: List of available models with status indicators

##### **Get Circuit Breakers**
- **Purpose**: View risk management and circuit breaker settings
- **Use Case**: Risk management review, safety configuration check
- **Response**: Current risk limits, stop-loss settings, safety parameters

##### **Live Trading Status**
- **Purpose**: Check live trading system capabilities
- **Use Case**: Verification before enabling live trading
- **Response**: Live trading readiness, API connectivity, account status

##### **Backtesting Info**
- **Purpose**: Access historical testing capabilities
- **Use Case**: Strategy validation, historical performance analysis
- **Response**: Available backtesting features and data ranges

##### **System Metrics (JSON)**
- **Purpose**: Detailed system performance data
- **Use Case**: Technical monitoring, performance optimization
- **Response**: Comprehensive metrics in JSON format

##### **Prometheus Metrics**
- **Purpose**: Metrics in Prometheus format for external monitoring
- **Use Case**: Integration with Grafana, advanced monitoring setups
- **Response**: Metrics formatted for Prometheus ingestion

## 🎯 Common Use Cases

### 1. Daily System Check

**Steps:**
1. Open dashboard: `http://localhost:8020/dashboard`
2. Verify **System Health** shows "Healthy" (green)
3. Check **AI Models** count matches expected (typically 20+ models)
4. Review **Trading Status** for yesterday's performance
5. Click **Check Models** to verify AI connectivity

### 2. Starting Paper Trading

**For Beginners:**
1. Click **"Start Paper Trading"** for basic simulation
2. Monitor the response for session ID and initial balance
3. Watch **Trading Status** panel for activity updates

**For Advanced Users:**
1. Click **"Start Advanced Paper Trading"** for full AI analysis
2. Review the response for available features and limitations
3. Monitor system metrics for performance impact

### 3. System Troubleshooting

**If System Shows "Degraded":**
1. Click **"Check Models"** to identify unavailable AI models
2. Click **"Get Circuit Breakers"** to verify risk management settings
3. Check **System Metrics** for resource constraints
4. Review logs: `docker-compose logs -f fenixai-trading-bot`

**If Trading Seems Inactive:**
1. Check **Trading Status** panel for current mode
2. Click **"Live Trading Status"** to verify connectivity
3. Verify API keys in `.env` file are correct
4. Click **"Get Circuit Breakers"** to check if safety limits triggered

### 4. Performance Monitoring

**Regular Monitoring:**
1. Check **System Metrics** for resource usage trends
2. Monitor **Trading Status** for win rate and performance
3. Use **"Prometheus Metrics"** for external monitoring integration
4. Review **"System Metrics (JSON)"** for detailed analysis

## 📊 Understanding Responses

### Successful Responses

**Green Indicators:**
- System status shows "Healthy"
- Trading operations return success messages
- Model checks show available models

**Example Success Response:**
```json
{
  "status": "success",
  "message": "Operation completed successfully",
  "data": { /* relevant data */ },
  "timestamp": "2025-07-20T20:00:00Z"
}
```

### Warning Responses

**Yellow Indicators:**
- System status shows "Degraded"  
- Partial functionality messages
- Some models unavailable

**Example Warning Response:**
```json
{
  "status": "partial",
  "message": "Some features limited",
  "available": ["basic_trading", "market_data"],
  "limited": ["advanced_ai", "full_analysis"]
}
```

### Error Responses

**Red Indicators:**
- System status shows "Unhealthy"
- Error messages in tool responses
- Failed connectivity tests

**Example Error Response:**
```json
{
  "status": "error",
  "message": "Service unavailable",
  "error_code": "CONNECTION_FAILED",
  "suggestion": "Check configuration and restart"
}
```

## 🔄 Auto-Refresh Behavior

The dashboard automatically refreshes every **10 seconds** to provide real-time updates:

- **System Health**: Updates automatically to reflect current status
- **Trading Status**: Shows real-time trading activity and performance
- **AI Models**: Reflects current model availability
- **System Metrics**: Updates with current resource usage

**Manual Refresh**: You can also manually refresh by clicking any tool button or refreshing the browser page.

## 🎨 Visual Indicators

### Color Coding System

| Color | Meaning | Applied To |
|-------|---------|------------|
| **🟢 Green** | Healthy/Success | System status, successful operations |
| **🟡 Yellow** | Warning/Degraded | Partial functionality, warnings |
| **🔴 Red** | Error/Critical | System failures, critical errors |
| **🔵 Blue** | Information | Normal status messages, data display |
| **⚫ Gray** | Inactive/Disabled | Stopped services, unavailable features |

### Status Icons

- **💚 Health Icon**: Overall system health
- **📊 Chart Icon**: Trading and performance data
- **🤖 Robot Icon**: AI and model status
- **🎮 Game Controller**: Interactive controls
- **🔧 Wrench Icon**: System tools and utilities
- **⚡ Lightning**: Real-time/active status
- **⏸️ Pause**: Inactive/paused status

## 🚨 Alerts and Notifications

### Dashboard Alerts

The dashboard may show alerts for:

- **API Connection Issues**: When Binance API is unreachable
- **Model Unavailability**: When AI models are not responding
- **Resource Limits**: When CPU/memory usage is high
- **Trading Halts**: When circuit breakers are triggered

### Response to Alerts

1. **Red System Health**: 
   - Check logs immediately
   - Verify configuration
   - Consider system restart

2. **Yellow Degraded Status**:
   - Monitor for improvement
   - Check individual components
   - Plan maintenance window

3. **Trading Stopped**:
   - Check market conditions
   - Verify API connectivity
   - Review risk management settings

## 📋 Best Practices

### Daily Operations

1. **Morning Check**:
   - Verify system health is green
   - Check overnight trading performance
   - Review any alerts or warnings

2. **During Trading Hours**:
   - Monitor trading status regularly
   - Watch for circuit breaker triggers
   - Keep an eye on system metrics

3. **End of Day**:
   - Review trading performance
   - Check system health before close
   - Plan any necessary maintenance

### Troubleshooting Workflow

1. **Identify Issue**: Use dashboard status indicators
2. **Gather Information**: Click relevant tool buttons for details
3. **Check Logs**: Use `docker-compose logs -f` for detailed information
4. **Take Action**: Restart services, fix configuration, or contact support
5. **Verify Fix**: Use dashboard to confirm resolution

## 🔗 Related Documentation

- **Docker Setup Guide**: `/docs/DOCKER_SETUP_GUIDE.md`
- **API Documentation**: `http://localhost:8020/docs`
- **Architecture Overview**: `/docs/ARCHITECTURE.md`
- **Installation Guide**: `/docs/INSTALL_GUIDE.md`

## 🆘 Support and Troubleshooting

If you experience issues with the dashboard:

1. **Verify URL**: Ensure you're accessing `http://localhost:8020/dashboard`
2. **Check Container Status**: Run `docker-compose ps`
3. **Review Logs**: Use `docker-compose logs -f fenixai-trading-bot`
4. **Test API**: Try `curl http://localhost:8020/health`
5. **Browser Issues**: Try clearing cache or using incognito mode

For persistent issues, check the troubleshooting section in the Docker Setup Guide or create an issue on GitHub with:
- Dashboard screenshot
- Browser console errors
- Container logs
- System configuration

---

**Happy Trading!** The FenixAI Dashboard is your command center for intelligent cryptocurrency trading. Use it wisely and monitor your system regularly for optimal performance.
