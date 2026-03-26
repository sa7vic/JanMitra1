import { useEffect, useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import { useParams } from 'react-router-dom';
import { AlertTriangle, Calendar, Loader2, MapPin, UserCheck } from 'lucide-react';
import {
  assignGovernmentReport,
  getEligibleAssignees,
  getReportDetail,
  updateGovernmentReportStatus,
} from '../lib/api';

const STATUS_META = {
  pending: { label: 'Pending', emoji: '🟡', cls: 'bg-yellow-100 text-yellow-800' },
  working: { label: 'Working', emoji: '🔵', cls: 'bg-blue-100 text-blue-800' },
  completed: { label: 'Completed', emoji: '🟢', cls: 'bg-green-100 text-green-800' },
};

const ReportDetail = () => {
  const { id } = useParams();

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const [report, setReport] = useState(null);
  const [permissions, setPermissions] = useState({ can_assign: false, can_update_status: false });
  const [auditLogs, setAuditLogs] = useState([]);
  const [assignees, setAssignees] = useState([]);

  const [selectedAssignee, setSelectedAssignee] = useState('');
  const [assignStatus, setAssignStatus] = useState('working');

  const statusInfo = useMemo(() => STATUS_META[report?.status] || STATUS_META.pending, [report?.status]);

  const refreshDetail = async () => {
    const data = await getReportDetail(id);
    setReport(data.report);
    setPermissions(data.permissions || { can_assign: false, can_update_status: false });
    setAuditLogs(data.audit_logs || []);
    if (data.report?.assigned_to) {
      setSelectedAssignee(String(data.report.assigned_to));
    }
  };

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError('');
      try {
        await refreshDetail();
        const usersData = await getEligibleAssignees(id);
        setAssignees(usersData.users || []);
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to load report detail');
      } finally {
        setLoading(false);
      }
    };

    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const handleAssign = async () => {
    if (!selectedAssignee) return;

    setSaving(true);
    setError('');
    try {
      // Optimistic status for snappy admin UX.
      const previous = report;
      setReport((prev) => (prev ? { ...prev, status: assignStatus, assigned_to: Number(selectedAssignee) } : prev));

      await assignGovernmentReport(id, {
        assigned_to: Number(selectedAssignee),
        status: assignStatus,
      });
      await refreshDetail();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to assign report');
      await refreshDetail();
    } finally {
      setSaving(false);
    }
  };

  const handleStatusUpdate = async (nextStatus) => {
    setSaving(true);
    setError('');
    try {
      const previous = report?.status;
      setReport((prev) => (prev ? { ...prev, status: nextStatus } : prev));

      await updateGovernmentReportStatus(id, nextStatus);
      await refreshDetail();
      if (previous === nextStatus) {
        setError('');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update status');
      await refreshDetail();
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-10 h-10 animate-spin text-primary-600" />
      </div>
    );
  }

  if (!report) {
    return (
      <div className="min-h-screen pt-20 px-4">
        <div className="max-w-3xl mx-auto bg-white border border-red-200 text-red-700 rounded-lg p-4">
          Report not found.
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 pt-20 pb-10 px-4">
      <div className="max-w-6xl mx-auto">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
          <div className="bg-white rounded-xl border border-gray-200 p-6 shadow">
            <div className="flex flex-wrap items-start justify-between gap-4 mb-4">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{report.title || 'Citizen Report'}</h1>
                <div className="text-sm text-gray-600 mt-1">
                  Report #{report.id}
                </div>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm font-semibold ${statusInfo.cls}`}>
                {statusInfo.emoji} {statusInfo.label}
              </span>
            </div>

            {error && (
              <div className="mb-4 bg-red-50 border border-red-200 text-red-700 rounded-lg p-3 text-sm">
                {error}
              </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 space-y-5">
                <div>
                  <h2 className="font-semibold text-gray-900 mb-2">Description</h2>
                  <p className="text-gray-700 whitespace-pre-wrap">{report.description || 'No description available.'}</p>
                </div>

                <div>
                  <h2 className="font-semibold text-gray-900 mb-2">Location</h2>
                  <div className="flex flex-wrap gap-2">
                    {report.state && <span className="px-2 py-1 text-xs rounded bg-slate-100 text-slate-700">{report.state}</span>}
                    {report.district && <span className="px-2 py-1 text-xs rounded bg-slate-100 text-slate-700">{report.district}</span>}
                    {report.city && <span className="px-2 py-1 text-xs rounded bg-slate-100 text-slate-700">{report.city}</span>}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm text-gray-600">
                  <div className="flex items-center gap-2"><MapPin className="w-4 h-4" />{report.location || 'Location not specified'}</div>
                  <div className="flex items-center gap-2"><Calendar className="w-4 h-4" />{new Date(report.created_at).toLocaleString()}</div>
                </div>

                <div>
                  <h2 className="font-semibold text-gray-900 mb-2">Image Evidence</h2>
                  {report.image_url ? (
                    <img src={report.image_url} alt="report" className="rounded-lg border border-gray-200 max-h-[420px] object-cover w-full" />
                  ) : (
                    <div className="p-4 border border-dashed border-gray-300 rounded-lg text-sm text-gray-500">No image uploaded.</div>
                  )}
                </div>
              </div>

              <div className="space-y-5">
                <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-900 mb-2">Assignment</h3>
                  <div className="text-sm text-gray-700 mb-3">
                    Assigned to:{' '}
                    {report.assigned_to_user ? (
                      <span className="font-semibold">
                        {report.assigned_to_user.name} - {report.assigned_to_user.gov_level} ({report.assigned_to_user.district || report.assigned_to_user.city || report.assigned_to_user.state || 'N/A'})
                      </span>
                    ) : (
                      <span className="text-gray-500">Unassigned</span>
                    )}
                  </div>

                  {permissions.can_assign && (
                    <div className="space-y-2">
                      <select
                        value={selectedAssignee}
                        onChange={(e) => setSelectedAssignee(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                      >
                        <option value="">Select officer</option>
                        {assignees.map((user) => (
                          <option key={user.id} value={user.id}>
                            {user.name} - {user.gov_level} ({user.district || user.city || user.state || 'N/A'})
                          </option>
                        ))}
                      </select>

                      <select
                        value={assignStatus}
                        onChange={(e) => setAssignStatus(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                      >
                        <option value="working">Set as Working</option>
                        <option value="pending">Keep Pending</option>
                        {report.status === 'working' && <option value="completed">Set as Completed</option>}
                      </select>

                      <button
                        onClick={handleAssign}
                        disabled={saving || !selectedAssignee}
                        className="w-full py-2.5 rounded-lg bg-indigo-600 text-white font-semibold text-sm disabled:opacity-50"
                      >
                        {saving ? 'Assigning...' : 'Assign'}
                      </button>
                    </div>
                  )}
                </div>

                <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-900 mb-2">Workflow Status</h3>
                  <div className="grid grid-cols-1 gap-2">
                    {['pending', 'working', 'completed'].map((status) => {
                      const meta = STATUS_META[status];
                      const disabled = saving || !permissions.can_update_status || report.status === status;
                      return (
                        <button
                          key={status}
                          onClick={() => handleStatusUpdate(status)}
                          disabled={disabled}
                          className={`w-full py-2 rounded-lg text-sm font-semibold border ${
                            report.status === status
                              ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                              : 'border-gray-300 bg-white text-gray-700'
                          } disabled:opacity-60`}
                        >
                          {meta.emoji} {meta.label}
                        </button>
                      );
                    })}
                  </div>
                  {!permissions.can_update_status && (
                    <div className="text-xs text-gray-500 mt-2 flex items-center gap-1">
                      <AlertTriangle className="w-3.5 h-3.5" />
                      You are not authorized to update this report status.
                    </div>
                  )}
                </div>

                <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                    <UserCheck className="w-4 h-4" />
                    Audit Log
                  </h3>
                  {auditLogs.length === 0 ? (
                    <div className="text-sm text-gray-500">No audit events yet.</div>
                  ) : (
                    <div className="space-y-2 max-h-56 overflow-auto">
                      {auditLogs.map((log) => (
                        <div key={log.id} className="text-xs text-gray-700 border border-gray-200 rounded-md p-2 bg-white">
                          <div className="font-semibold">{log.actor_name || 'Officer'} - {log.action}</div>
                          <div className="text-gray-600">{new Date(log.created_at).toLocaleString()}</div>
                          {log.from_status && log.to_status && (
                            <div>Status: {log.from_status} → {log.to_status}</div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default ReportDetail;
