// MCP Actions Logging Framework

import fs from 'fs';
import path from 'path';

/**
 * Log an action with timestamp, status, and details
 * @param {string} action - The action being performed
 * @param {Object} details - Details about the action
 * @param {string} status - Status of the action (SUCCESS, FAILED, EXECUTING, etc.)
 * @param {string} service - The service performing the action (linkedin, twitter, odoo)
 */
function logAction(action, details, status, service = 'generic') {
  const timestamp = new Date().toISOString();
  const logEntry = `[${timestamp}] [${service.toUpperCase()}] ${status} - ${action}: ${JSON.stringify(details)}\n`;

  // Determine log file based on service
  const logDir = path.join(process.env.HOME, 'AI_Employee_Vault', 'Logs');

  // Ensure log directory exists
  if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir, { recursive: true });
  }

  const logFile = path.join(logDir, `${service}_actions.log`);
  fs.appendFileSync(logFile, logEntry);

  // Also log to console
  console.log(logEntry.trim());
}

/**
 * Log a successful action
 * @param {string} action - The action that succeeded
 * @param {Object} details - Details about the successful action
 * @param {string} service - The service that performed the action
 */
function logSuccess(action, details, service = 'generic') {
  logAction(action, details, 'SUCCESS', service);
}

/**
 * Log a failed action
 * @param {string} action - The action that failed
 * @param {Object} details - Details about the failure
 * @param {string} service - The service that experienced the failure
 */
function logFailure(action, details, service = 'generic') {
  logAction(action, details, 'FAILED', service);
}

/**
 * Log an executing action
 * @param {string} action - The action being executed
 * @param {Object} details - Details about the action being executed
 * @param {string} service - The service performing the action
 */
function logExecuting(action, details, service = 'generic') {
  logAction(action, details, 'EXECUTING', service);
}

/**
 * Get log entries for a specific service within a time range
 * @param {string} service - The service to get logs for
 * @param {Date} startTime - Start time for log retrieval
 * @param {Date} endTime - End time for log retrieval
 * @returns {Array} Array of log entries
 */
function getLogEntries(service, startTime, endTime) {
  const logDir = path.join(process.env.HOME, 'AI_Employee_Vault', 'Logs');
  const logFile = path.join(logDir, `${service}_actions.log`);

  if (!fs.existsSync(logFile)) {
    return [];
  }

  const logContent = fs.readFileSync(logFile, 'utf8');
  const logLines = logContent.split('\n').filter(line => line.trim() !== '');

  const filteredLogs = [];
  for (const line of logLines) {
    // Extract timestamp from log line
    const timestampMatch = line.match(/\[(.*?)\]/);
    if (timestampMatch) {
      const timestamp = new Date(timestampMatch[1]);
      if (timestamp >= startTime && timestamp <= endTime) {
        filteredLogs.push(line);
      }
    }
  }

  return filteredLogs;
}

/**
 * Initialize logging system by ensuring log directory exists
 */
function initializeLogging() {
  const logDir = path.join(process.env.HOME, 'AI_Employee_Vault', 'Logs');
  if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir, { recursive: true });
  }
}

export {
  logAction,
  logSuccess,
  logFailure,
  logExecuting,
  getLogEntries,
  initializeLogging
};