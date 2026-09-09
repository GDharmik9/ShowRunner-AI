import { useState, useEffect, useRef } from 'react';

// Custom lightweight inline icons mapping to Lucide designs
const CpuIcon = ({ className }) => (
  <svg
    className={className}
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <rect
      width="16"
      height="16"
      x="4"
      y="4"
      rx="2"
    />
    <rect
      width="6"
      height="6"
      x="9"
      y="9"
      rx="1"
    />
    <path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 15h3M1 9h3M1 15h3" />
  </svg>
);

const ActivityIcon = ({ className }) => (
  <svg
    className={className}
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
  </svg>
);

const TerminalIcon = ({ className }) => (
  <svg
    className={className}
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <polyline points="4 17 10 11 4 5" />
    <line
      x1="12"
      x2="20"
      y1="19"
      y2="19"
    />
  </svg>
);

const ShieldIcon = ({ className }) => (
  <svg
    className={className}
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M20 13c0 5-3.5 7.5-7.66 9.7a1 1 0 0 1-.68 0C7.5 20.5 4 18 4 13V6a1 1 0 0 1 .76-.97l8-2a1 1 0 0 1 .48 0l8 2A1 1 0 0 1 20 6z" />
  </svg>
);

const AlertCircleIcon = ({ className }) => (
  <svg
    className={className}
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <circle
      cx="12"
      cy="12"
      r="10"
    />
    <line
      x1="12"
      x2="12"
      y1="8"
      y2="12"
    />
    <line
      x1="12"
      x2="12.01"
      y1="16"
      y2="16"
    />
  </svg>
);

const ThermometerIcon = ({ className }) => (
  <svg
    className={className}
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z" />
  </svg>
);

const PlayIcon = ({ className }) => (
  <svg
    className={className}
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <polygon points="6 3 20 12 6 21 6 3" />
  </svg>
);

const ServerIcon = ({ className }) => (
  <svg
    className={className}
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <rect
      width="20"
      height="8"
      x="2"
      y="2"
      rx="2"
      ry="2"
    />
    <rect
      width="20"
      height="8"
      x="2"
      y="14"
      rx="2"
      ry="2"
    />
    <line
      x1="6"
      x2="6.01"
      y1="6"
      y2="6"
    />
    <line
      x1="6"
      x2="6.01"
      y1="18"
      y2="18"
    />
    <line
      x1="10"
      x2="10.01"
      y1="6"
      y2="6"
    />
    <line
      x1="10"
      x2="10.01"
      y1="18"
      y2="18"
    />
  </svg>
);

const SendIcon = ({ className }) => (
  <svg
    className={className}
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <line
      x1="22"
      x2="11"
      y1="2"
      y2="13"
    />
    <polygon points="22 2 15 22 11 13 2 9 22 2" />
  </svg>
);

export default function StudioCommandCenter() {
  // Initial Nodes Dataset aligning with telemetry_emitter.py configurations
  const initialNodes = [
    {
      id: 'node-01',
      name: 'Node 1',
      engine: 'Blender',
      profile: 'GRID_RTX6000-12Q',
      vramUsed: 6.7,
      vramTotal: 12.0,
      gpuUtil: 95,
      temp: 72,
      task: 'VFX_BATTLE_012_LIGHT',
      status: 'HEALTHY',
    },
    {
      id: 'node-02',
      name: 'Node 2',
      engine: 'Blender',
      profile: 'GRID_RTX6000-12Q',
      vramUsed: 7.0,
      vramTotal: 12.0,
      gpuUtil: 90,
      temp: 70,
      task: 'VFX_BATTLE_012_COMP',
      status: 'HEALTHY',
    },
    {
      id: 'node-03',
      name: 'Node 3',
      engine: 'Blender',
      profile: 'GRID_RTX6000-24Q',
      vramUsed: 14.3,
      vramTotal: 24.0,
      gpuUtil: 92,
      temp: 78,
      task: 'VFX_BATTLE_013_GEO',
      status: 'HEALTHY',
    },
    {
      id: 'node-04',
      name: 'Node 4',
      engine: 'Unreal Engine',
      profile: 'GRID_RTX6000-24Q',
      vramUsed: 17.2,
      vramTotal: 24.0,
      gpuUtil: 97,
      temp: 81,
      task: 'VFX_BATTLE_014_RENDER',
      status: 'HEALTHY',
    },
    {
      id: 'node-05',
      name: 'Node 5',
      engine: 'Unreal Engine',
      profile: 'GRID_RTX6000-12Q',
      vramUsed: 8.5,
      vramTotal: 12.0,
      gpuUtil: 88,
      temp: 74,
      task: 'VFX_BATTLE_015_ANIM',
      status: 'HEALTHY',
    },
    {
      id: 'node-06',
      name: 'Node 6',
      engine: 'Unreal Engine',
      profile: 'GRID_RTX6000-12Q',
      vramUsed: 8.4,
      vramTotal: 12.0,
      gpuUtil: 88,
      temp: 73,
      task: 'VFX_BATTLE_015_FX',
      status: 'HEALTHY',
    },
  ];

  const [nodes, setNodes] = useState(initialNodes);
  const [alerts, setAlerts] = useState([
    {
      id: 'a1',
      severity: 'info',
      title: 'Grafana Alloy Active',
      text: 'Scraping metrics & logs from 6 virtualised nodes.',
      time: 'Just now',
    },
  ]);
  const [timeline, setTimeline] = useState([
    {
      id: 't1',
      type: 'system',
      title: 'Guardian Core Initialised',
      desc: 'Showrunner AI Technical Director standing by to protect cluster.',
      time: '10 mins ago',
    },
  ]);
  const [chatLog, setChatLog] = useState([
    {
      id: 'm1',
      sender: 'assistant',
      text: 'Salutations. I am the Showrunner AI Technical Director. I monitor GPU telemetry, VRAM overheads, and Arnold/Loki log streams across our 6-node virtual render farm. How can I protect the pipeline today?',
    },
  ]);
  const [chatInput, setChatInput] = useState('');
  const [isInjecting, setIsInjecting] = useState(false);
  const [activeAlertCount, setActiveAlertCount] = useState(0);

  const timelineEndRef = useRef(null);
  const chatEndRef = useRef(null);

  useEffect(() => {
    timelineEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [timeline]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatLog]);

  // Demo Trigger: CUDA OOM Injection Workflow (aligns perfectly with failure mode matrix!)
  const handleInjectCUDA_OOM = () => {
    if (isInjecting) return;
    setIsInjecting(true);

    // Step 1: Push VRAM to max allocation and trigger Warning
    setNodes((prev) =>
      prev.map((node) =>
        node.id === 'node-04'
          ? {
              ...node,
              vramUsed: 24.0,
              gpuUtil: 100,
              temp: 88,
              status: 'WARNING',
            }
          : node,
      ),
    );

    setAlerts((prev) => [
      {
        id: 'oom-1',
        severity: 'warning',
        title: 'VRAM Threshold Breached',
        text: 'Node 4 GPU memory utilization is at 100%. Critical bounds reached.',
        time: '0s ago',
      },
      ...prev,
    ]);

    setTimeline((prev) => [
      ...prev,
      {
        id: `t-${Date.now()}-1`,
        type: 'alert',
        title: 'Prometheus Alert Fired',
        desc: 'nvidia_smi_vgpu_fb_used_bytes == nvidia_smi_vgpu_fb_total_bytes on Node 4',
        time: '0s',
      },
    ]);

    // Step 2: Simulate complete render failure
    setTimeout(() => {
      setNodes((prev) =>
        prev.map((node) =>
          node.id === 'node-04'
            ? {
                ...node,
                vramUsed: 24.0,
                gpuUtil: 0,
                temp: 45,
                status: 'CRASHED_OOM',
                task: 'CRASHED (VFX_BATTLE_014_RENDER)',
              }
            : node,
        ),
      );

      setAlerts((prev) => [
        {
          id: 'oom-2',
          severity: 'critical',
          title: 'CUDA Out Of Memory',
          text: 'CRITICAL error: CUDA_ERROR_OUT_OF_MEMORY: Shot VFX_BATTLE_014 failed on Node 4.',
          time: '2s ago',
        },
        ...prev,
      ]);
      setActiveAlertCount(1);

      setTimeline((prev) => [
        ...prev,
        {
          id: `t-${Date.now()}-2`,
          type: 'analysis',
          title: 'Loki Diagnostic Pattern Scan',
          desc: 'Identified matching traceback: "Arnold GPU device out of memory" in render logs.',
          time: '2s',
        },
      ]);
    }, 1500);

    // Step 3: Showrunner AI reasons on metrics + log correlation, executes dynamic config change
    setTimeout(() => {
      setTimeline((prev) => [
        ...prev,
        {
          id: `t-${Date.now()}-3`,
          type: 'decision',
          title: 'Remediation Formulated',
          desc: 'Correlated VRAM flatline with Loki OOM log signatures. Executing switch to Tiled Rendering Config (64x64 blocks).',
          time: '4s',
        },
      ]);
    }, 3500);

    // Step 4: Call Mock API Node Config Switch
    setTimeout(() => {
      setTimeline((prev) => [
        ...prev,
        {
          id: `t-${Date.now()}-4`,
          type: 'remediation',
          title: 'Queue Webhook Dispatched',
          desc: 'PATCH request sent to queue-manager api updates job renderer config to "tiled".',
          time: '6s',
        },
      ]);
    }, 5000);

    // Step 5: Node recovers and operates in tiled fallback
    setTimeout(() => {
      setNodes((prev) =>
        prev.map((node) =>
          node.id === 'node-04'
            ? {
                ...node,
                vramUsed: 9.2,
                gpuUtil: 84,
                temp: 73,
                status: 'HEALTHY',
                task: 'VFX_BATTLE_014_RENDER (TILED_64x64)',
              }
            : node,
        ),
      );

      setAlerts((prev) => prev.filter((a) => !a.id.startsWith('oom')));
      setActiveAlertCount(0);

      setTimeline((prev) => [
        ...prev,
        {
          id: `t-${Date.now()}-5`,
          type: 'resolution',
          title: 'System Restored',
          desc: 'Node 4 healthy under tiled render load. Core allocations reduced from 24GB to 9.2GB VRAM.',
          time: '8s',
        },
      ]);

      setChatLog((prev) => [
        ...prev,
        {
          id: `chat-${Date.now()}`,
          sender: 'assistant',
          text: '🚨 [AUTO-REMEDIATION REPORT] I detected an extreme CUDA VRAM saturation on Node 4 during render job VFX_BATTLE_014. By scanning the Loki log streams and confirming "CUDA_ERROR_OUT_OF_MEMORY", I executed a configuration swap via our studio queue manager. Node 4 is now fully operational rendering with 64x64 Tiles, bringing active VRAM down to 9.2GB.',
        },
      ]);

      setIsInjecting(false);
    }, 7000);
  };

  // Demo Trigger: Thread Deadlock Injection Workflow
  const handleInjectDeadlock = () => {
    if (isInjecting) return;
    setIsInjecting(true);

    // Step 1: Peg CPU to max, drop GPU utilization, task hangs
    setNodes((prev) =>
      prev.map((node) =>
        node.id === 'node-03'
          ? { ...node, gpuUtil: 0, temp: 84, status: 'DEADLOCKED' }
          : node,
      ),
    );

    setAlerts((prev) => [
      {
        id: 'dl-1',
        severity: 'warning',
        title: 'Node Deadlock Warning',
        text: 'Node 3 CPU usage at 100% while GPU utilisation is 0%. Possible execution hang.',
        time: '0s ago',
      },
      ...prev,
    ]);

    setTimeline((prev) => [
      ...prev,
      {
        id: `t-${Date.now()}-dl1`,
        type: 'alert',
        title: 'Deadlock Metric Sig Fired',
        desc: 'Prometheus rule: node_cpu_utilization == 100 && gpu_utilization == 0 active.',
        time: '0s',
      },
    ]);

    // Step 2: Showrunner agent steps in to query system locks
    setTimeout(() => {
      setTimeline((prev) => [
        ...prev,
        {
          id: `t-${Date.now()}-dl2`,
          type: 'analysis',
          title: 'Pyroscope Profile Scrape',
          desc: 'Active continuous thread traces show prolonged lock durations on parallel Arnold CPU synchronization spans.',
          time: '2s',
        },
      ]);
    }, 1500);

    // Step 3: Decision to reboot node
    setTimeout(() => {
      setTimeline((prev) => [
        ...prev,
        {
          id: `t-${Date.now()}-dl3`,
          type: 'decision',
          title: 'Force Process Reboot Triggered',
          desc: 'Deadlock confirmed via continuous profiling lock waits. Command dispatched to drop node and reboot hypervisor daemon.',
          time: '3.5s',
        },
      ]);
    }, 3500);

    // Step 4: Fire Remediation POST reboot hook
    setTimeout(() => {
      setTimeline((prev) => [
        ...prev,
        {
          id: `t-${Date.now()}-dl4`,
          type: 'remediation',
          title: 'Hard Restart Webhook Fired',
          desc: 'POST request sent to hypervisor manager: /nodes/node-03/restart executed.',
          time: '5.0s',
        },
      ]);
    }, 5000);

    // Step 5: System restores to healthy
    setTimeout(() => {
      setNodes((prev) =>
        prev.map((node) =>
          node.id === 'node-03'
            ? {
                ...node,
                vramUsed: 0.0,
                gpuUtil: 0,
                temp: 35,
                status: 'HEALTHY',
                task: 'IDLE (QUEUED_FOR_GEO)',
              }
            : node,
        ),
      );

      setAlerts((prev) => prev.filter((a) => !a.id.startsWith('dl')));

      setTimeline((prev) => [
        ...prev,
        {
          id: `t-${Date.now()}-dl5`,
          type: 'resolution',
          title: 'VM Daemon Restored',
          desc: 'Node 3 hypervisor hard reboot complete. Running processes flushed. Ready for job re-allocation.',
          time: '7s',
        },
      ]);

      setChatLog((prev) => [
        ...prev,
        {
          id: `chat-dl-${Date.now()}`,
          sender: 'assistant',
          text: '🛠️ [AUTO-REMEDIATION REPORT] Thread deadlock resolved on Node 3 (Blender). After confirming CPU pinning and flatlining GPU utilization, continuous profiling scans isolated thread synchronization mutex blocks. A VM daemon restart was successfully executed to flush memory registers and release GPU engines.',
        },
      ]);

      setIsInjecting(false);
    }, 7000);
  };

  // Chat Submission Handler
  const handleSendChat = (textToSend = chatInput) => {
    const cleanText = textToSend.trim();
    if (!cleanText) return;

    const userMessage = {
      id: `msg-${Date.now()}`,
      sender: 'user',
      text: cleanText,
    };
    setChatLog((prev) => [...prev, userMessage]);
    setChatInput('');

    // Simulated responses matching pre-set director audit commands
    setTimeout(() => {
      let responseText = '';
      const textLower = cleanText.toLowerCase();

      if (textLower.includes('audit node 4')) {
        const n4 = nodes.find((n) => n.id === 'node-04');
        responseText = `🔍 **Node 4 Audit Report:**\n- **Renderer Profile:** ${n4.profile} (24GB VRAM)\n- **Render Engine:** ${n4.engine}\n- **Telemetry:** ${n4.gpuUtil}% GPU Utilization | ${n4.vramUsed}/${n4.vramTotal} GB VRAM Used\n- **Temp Profile:** ${n4.temp}°C\n- **Current Task:** "${n4.task}"\n- **Status:** [${n4.status}]\n- **SRE Insight:** Telemetry indices indicate healthy frame completion rates. Running normal baseline load. No memory bottlenecks detected.`;
      } else if (textLower.includes('morning briefing')) {
        responseText = `☀️ **Morning Briefing: Showrunner AI Status Report (07:00 Pipeline Sync)**\n\n**1. Cluster State Overview:**\n- Total Nodes Online: 6 / 6 (100% Availability)\n- Global Compute Overhead: 91.5% GPU utilization\n- Asset Cache HIT Rate: 94.2% (healthy I/O limits)\n\n**2. Action History (Last 12 Hours):**\n- ✅ **02:14 AM**: Blocked CUDA OOM on Node 4 by auto-switching Unreal configuration to tiled frames (Saved approx. 4.5 rendering hours).\n- ✅ **05:43 AM**: Resolved parallel pipeline lock hanging on Node 3 by cycling the hypervisor daemon.\n\nEverything is operational for the VFX sync team.`;
      } else if (
        textLower.includes('clear alerts') ||
        textLower.includes('reset')
      ) {
        setNodes(initialNodes);
        setAlerts([
          {
            id: 'a1',
            severity: 'info',
            title: 'Grafana Alloy Active',
            text: 'Scraping metrics & logs from 6 virtualised nodes.',
            time: 'Just now',
          },
        ]);
        responseText =
          '🔄 Reset request processed. Telemetry logs and node status indicators have been restored to default healthy baselines.';
      } else {
        responseText = `Understood. Processing request: "${cleanText}". I will query Grafana Cloud's metrics (Prometheus) and logs (Loki) via my MCP interfaces to deliver structural context. Is there a specific rendering failure signature or active node you would like me to audit?`;
      }

      setChatLog((prev) => [
        ...prev,
        { id: `bot-${Date.now()}`, sender: 'assistant', text: responseText },
      ]);
    }, 1000);
  };

  return (
    <div className="h-full min-h-0 bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-slate-950">
      {/* Top Engineering Nav Bar */}
      <header className="border-b border-slate-900 bg-slate-950/80 backdrop-blur-md px-6 py-4 flex items-center justify-between sticky top-0 z-50 max-h-[100px] shrink-0">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 bg-cyan-500/10 border border-cyan-500/30 rounded-lg flex items-center justify-center text-cyan-400">
            <ShieldIcon className="h-5 w-5 animate-pulse" />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight text-white flex items-center gap-2 m-0 ">
              SHOWRUNNER AI{' '}
              <span className="text-xs bg-cyan-500/15 text-cyan-400 border border-cyan-500/20 px-2 py-0.5 rounded font-mono">
                BETA v1.2
              </span>
            </h1>
            <p className="text-xs text-slate-500 m-0 font-mono">
              Autonomous VFX Render Farm Guardian & Remediation Dashboard
            </p>
          </div>
        </div>

        {/* Demo Execution / SRE Action Controls */}
        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-500 hidden md:inline font-mono">
            DEMO INJECTION SUITE:
          </span>
          <button
            onClick={handleInjectCUDA_OOM}
            disabled={isInjecting}
            className={`px-3 py-1.5 rounded text-xs font-semibold flex items-center gap-1.5 border transition ${
              isInjecting
                ? 'bg-slate-900 border-slate-800 text-slate-600 cursor-not-allowed'
                : 'bg-red-500/10 border-red-500/30 text-red-400 hover:bg-red-500/20 hover:border-red-500/50'
            }`}
          >
            <AlertCircleIcon className="h-3.5 w-3.5" />
            Inject CUDA OOM (Node 4)
          </button>
          <button
            onClick={handleInjectDeadlock}
            disabled={isInjecting}
            className={`px-3 py-1.5 rounded text-xs font-semibold flex items-center gap-1.5 border transition ${
              isInjecting
                ? 'bg-slate-900 border-slate-800 text-slate-600 cursor-not-allowed'
                : 'bg-amber-500/10 border-amber-500/30 text-amber-400 hover:bg-amber-500/20 hover:border-amber-500/50'
            }`}
          >
            <CpuIcon className="h-3.5 w-3.5" />
            Inject Deadlock (Node 3)
          </button>
          <button
            onClick={() => handleSendChat('Reset cluster status')}
            className="p-1.5 rounded border border-slate-800 text-slate-400 hover:text-white hover:bg-slate-900 transition"
            title="Reset Cluster"
          >
            <svg
              className="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 1121.21 15H18"
              />
            </svg>
          </button>
        </div>
      </header>
      {/* three columns section: left column = director chat console, center = main grid workspace layout, right column = timeline & alerts */}
      <section className="flex-1 min-h-0 flex flex-col md:flex-row overflow-y-auto md:overflow-hidden">
        {/* Section 4: Director Chat Console */}
        <div
          className="border border-slate-900 rounded-xl bg-slate-900/20 p-5 flex flex-col min-h-[420px] md:min-h-0 md:flex-1 md:overflow-hidden
        md:max-w-[350px] lg:max-w-[400px] xl:max-w-[450px] shrink-0 "
        >
          <div className="flex items-center justify-between pb-2 border-b border-slate-900 mb-3 shrink-0">
            <div className="flex items-center gap-2">
              <TerminalIcon className="h-4 w-4 text-cyan-400" />
              <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Director AI Chat Console
              </h2>
            </div>
          </div>

          {/* Conversation Log */}
          <div className="flex-1 min-h-0 overflow-y-auto space-y-3 mb-4 pr-1 text-xs select-text scrollbar-hidden">
            {chatLog.map((msg) => (
              <div
                key={msg.id}
                className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
              >
                <span className="text-[10px] text-slate-600 mb-1 font-mono uppercase tracking-wider">
                  {msg.sender === 'user'
                    ? 'VFX Lead (Director)'
                    : 'Showrunner AI Agent'}
                </span>
                <div
                  className={`p-3 rounded-xl max-w-[90%] whitespace-pre-wrap leading-relaxed ${
                    msg.sender === 'user'
                      ? 'bg-cyan-500 text-slate-950 font-medium'
                      : 'bg-slate-950/80 border border-slate-900 text-slate-300'
                  }`}
                >
                  {msg.text}
                </div>
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>

          {/* Pre-set Director Prompt Fast-Triggers */}
          <div className="mb-3 shrink-0">
            <p className="text-[9px] text-slate-600 font-mono uppercase tracking-wider mb-1.5">
              Quick Directives:
            </p>
            <div className="flex flex-wrap gap-1.5">
              <button
                onClick={() => handleSendChat('Audit Node 4 health')}
                className="px-2 py-1 rounded bg-slate-950 border border-slate-900 text-[10px] text-cyan-400 hover:bg-slate-900 hover:border-slate-800 transition"
              >
                "Audit Node 4 health"
              </button>
              <button
                onClick={() =>
                  handleSendChat('Prepare morning briefing for VFX lead')
                }
                className="px-2 py-1 rounded bg-slate-950 border border-slate-900 text-[10px] text-cyan-400 hover:bg-slate-900 hover:border-slate-800 transition"
              >
                "Prepare morning briefing"
              </button>
            </div>
          </div>

          {/* Natural Language Input Panel */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendChat();
            }}
            className="flex items-center gap-2 border border-slate-900 bg-slate-950 rounded-xl p-1 shrink-0 focus-within:border-cyan-500/50 transition-colors"
          >
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder="Instruct the Showrunner agent..."
              className="bg-transparent border-0 ring-0 focus:ring-0 flex-1 px-3 py-2 text-xs text-slate-100 placeholder-slate-600 outline-none"
            />
            <button
              type="submit"
              className="h-8 w-8 bg-cyan-500 hover:bg-cyan-400 rounded-lg flex items-center justify-center text-slate-950 transition"
            >
              <SendIcon className="h-4 w-4" />
            </button>
          </form>
        </div>

        {/* Main Grid Workspace Layout */}

        <main className="flex-1 min-h-0 min-w-0 overflow-y-auto p-6 pt-2 pb-0 grid grid-cols-1 xl:grid-cols-3 gap-6 m-0 w-full ">
          {/* Left Column: Node Health Overview & Embedded Metrics (Span 3/4) */}
          <div className="xl:col-span-3 flex flex-col gap-6">
            {/* section 1: Cluster Health Overview (6 Cards) */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                  <ServerIcon className="h-4 w-4 text-cyan-400" />
                  Cluster Node Status Overview
                </h2>
                <div className="flex items-center gap-2 text-xs">
                  <span className="flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>{' '}
                    6 Online
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {nodes.map((node) => {
                  const isHealthy = node.status === 'HEALTHY';
                  const isWarning = node.status === 'WARNING';
                  const isCrashed = node.status === 'CRASHED_OOM';
                  const isDeadlocked = node.status === 'DEADLOCKED';

                  return (
                    <div
                      key={node.id}
                      className={`rounded-xl border p-4 transition-all duration-300 bg-slate-900/50 relative overflow-hidden ${
                        isCrashed
                          ? 'border-red-500/40 shadow-lg shadow-red-500/5 bg-red-950/5'
                          : isDeadlocked
                            ? 'border-amber-500/40 shadow-lg shadow-amber-500/5 bg-amber-950/5'
                            : isWarning
                              ? 'border-amber-500/40 shadow-lg shadow-amber-500/5'
                              : 'border-slate-900 hover:border-slate-800 hover:bg-slate-900/80'
                      }`}
                    >
                      {/* Header: Name, Engine, Status Badge */}
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h3 className="font-bold text-white text-sm flex items-center gap-2">
                            {node.name}
                            <span className="text-[10px] font-mono text-slate-500">
                              {node.profile.split('-')[1]}
                            </span>
                          </h3>
                          <p className="text-xs text-slate-400">
                            {node.engine}
                          </p>
                        </div>

                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase ${
                            isHealthy
                              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/25'
                              : isCrashed
                                ? 'bg-red-500/10 text-red-400 border border-red-500/25 animate-pulse'
                                : 'bg-amber-500/10 text-amber-400 border border-amber-500/25 animate-pulse'
                          }`}
                        >
                          {node.status}
                        </span>
                      </div>

                      {/* GPU Utilization Bar */}
                      <div className="space-y-1 mb-3">
                        <div className="flex justify-between text-xs">
                          <span className="text-slate-400">GPU Core Util</span>
                          <span className="font-mono text-white">
                            {node.gpuUtil}%
                          </span>
                        </div>
                        <div className="h-1.5 bg-slate-950 rounded-full overflow-hidden">
                          <div
                            className={`h-full transition-all duration-500 ${
                              isCrashed
                                ? 'bg-red-500'
                                : node.gpuUtil > 90
                                  ? 'bg-cyan-400'
                                  : 'bg-slate-700'
                            }`}
                            style={{ width: `${node.gpuUtil}%` }}
                          />
                        </div>
                      </div>

                      {/* VRAM Utilization Slider */}
                      <div className="space-y-1 mb-3">
                        <div className="flex justify-between text-xs">
                          <span className="text-slate-400">
                            VRAM Allocation
                          </span>
                          <span className="font-mono text-white">
                            {node.vramUsed.toFixed(1)} /{' '}
                            {node.vramTotal.toFixed(1)} GB
                          </span>
                        </div>
                        <div className="h-1.5 bg-slate-950 rounded-full overflow-hidden">
                          <div
                            className={`h-full transition-all duration-500 ${
                              isCrashed
                                ? 'bg-red-500'
                                : node.vramUsed / node.vramTotal > 0.8
                                  ? 'bg-amber-500'
                                  : 'bg-cyan-500'
                            }`}
                            style={{
                              width: `${(node.vramUsed / node.vramTotal) * 100}%`,
                            }}
                          />
                        </div>
                      </div>

                      {/* Meta Fields: Temperature & Active Task */}
                      <div className="pt-2 border-t border-slate-950/80 flex items-center justify-between gap-3 text-[11px]">
                        <div className="flex items-center gap-1 text-slate-400 font-mono">
                          <ThermometerIcon
                            className={`h-3 w-3 ${node.temp > 80 ? 'text-red-400' : 'text-slate-400'}`}
                          />
                          <span>{node.temp}°C</span>
                        </div>
                        <div className="text-slate-400 truncate max-w-[140px] flex items-center gap-1">
                          <PlayIcon className="h-2.5 w-2.5 shrink-0" />
                          <span className="truncate font-mono">
                            {node.task}
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Section 2: Embedded Live Panel (Grafana Metrics & Loki Alerts) */}
            <div className="border border-slate-900 rounded-xl bg-slate-900/20 p-5 flex-1 flex flex-col max-h-[380px]">
              <div className="flex items-center justify-between pb-3 border-b border-slate-900 mb-4">
                <div className="flex items-center gap-2">
                  <ActivityIcon className="h-4 w-4 text-cyan-400" />
                  <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                    Grafana Cloud Telemetry Hub (Alloy Ingest)
                  </h2>
                </div>
                <div className="flex items-center gap-4 text-xs font-mono">
                  <span className="text-slate-400">
                    Scrape Rate: <span className="text-cyan-400">10s</span>
                  </span>
                  <span className="text-slate-400">
                    API Endpoint:{' '}
                    <span className="text-slate-400">/loki/api/v1/push</span>
                  </span>
                </div>
              </div>

              {/* Split Panel: Metrics Visualization & Live Loki Logger */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 flex-1">
                {/* Graphic Metric Simulation Component */}
                <div className="bg-slate-950/80 border border-slate-900/60 rounded-xl p-4 flex flex-col justify-between">
                  <div>
                    <span className="text-[10px] text-cyan-500 font-mono tracking-wider uppercase block mb-1">
                      PROMETHEUS TIME-SERIES
                    </span>
                    <h3 className="text-sm font-bold text-white mb-3">
                      Cluster VRAM vs Render Latency
                    </h3>
                  </div>

                  {/* Visual SVG Mock Chart */}
                  <div className="h-32 w-full flex items-end gap-1.5 relative py-2">
                    <div className="absolute inset-0 flex flex-col justify-between text-[9px] text-slate-600 font-mono pointer-events-none border-b border-slate-900 pb-1">
                      <div className="border-t border-slate-900/50 w-full pt-1">
                        24 GB (VRAM peak)
                      </div>
                      <div className="border-t border-slate-900/50 w-full pt-1">
                        12 GB (Average)
                      </div>
                      <div>0 GB</div>
                    </div>

                    {/* Mock Time Bars */}
                    <div className="flex-1 bg-slate-900/60 h-2/3 rounded-t hover:bg-slate-800 transition"></div>
                    <div className="flex-1 bg-slate-900/60 h-3/5 rounded-t hover:bg-slate-800 transition"></div>
                    <div className="flex-1 bg-slate-900/60 h-2/3 rounded-t hover:bg-slate-800 transition"></div>
                    <div className="flex-1 bg-slate-900/60 h-[70%] rounded-t hover:bg-slate-800 transition"></div>
                    <div className="flex-1 bg-slate-900/60 h-4/5 rounded-t hover:bg-slate-800 transition"></div>
                    {/* Dynamic failing bar during injection */}
                    <div
                      className={`flex-1 transition-all duration-500 rounded-t ${activeAlertCount > 0 ? 'bg-red-500 h-full animate-pulse' : 'bg-cyan-500 h-[75%]'}`}
                    ></div>
                    <div className="flex-1 bg-cyan-500/40 h-2/3 rounded-t"></div>
                  </div>

                  <div className="flex items-center gap-4 text-xs font-mono text-slate-500 pt-3 border-t border-slate-900/40">
                    <span className="flex items-center gap-1.5">
                      <span className="h-2 w-2 rounded-full bg-cyan-500"></span>{' '}
                      Mean Latency: 12.4s
                    </span>
                    <span className="flex items-center gap-1.5">
                      <span
                        className={`h-2 w-2 rounded-full ${activeAlertCount > 0 ? 'bg-red-500 animate-ping' : 'bg-slate-600'}`}
                      ></span>{' '}
                      Loki Alerts: {activeAlertCount} active
                    </span>
                  </div>
                </div>

                {/* Loki Log Alerts Container */}
                <div className="bg-slate-950/80 border border-slate-900/60 rounded-xl p-4 flex flex-col justify-between">
                  <div>
                    <span className="text-[10px] text-red-400 font-mono tracking-wider uppercase block mb-1">
                      LIVE LOKI INGEST STREAM
                    </span>
                    <h3 className="text-sm font-bold text-white mb-2">
                      Ingestion Warnings & Failures
                    </h3>
                  </div>

                  {/* Log Line Rows */}
                  <div className="flex-1 overflow-y-auto space-y-2 max-h-[140px] pr-2 font-mono text-[11px] leading-relaxed select-text mt-2">
                    {alerts.map((alert) => {
                      const isCrit = alert.severity === 'critical';
                      const isWarn = alert.severity === 'warning';
                      return (
                        <div
                          key={alert.id}
                          className={`p-2 rounded border leading-relaxed ${
                            isCrit
                              ? 'bg-red-500/5 border-red-500/25 text-red-400'
                              : isWarn
                                ? 'bg-amber-500/5 border-amber-500/25 text-amber-400'
                                : 'bg-slate-900/40 border-slate-900 text-slate-400'
                          }`}
                        >
                          <div className="flex justify-between font-bold mb-0.5 text-[10px]">
                            <span className="uppercase tracking-widest">
                              {alert.severity}
                            </span>
                            <span className="opacity-60 font-normal">
                              {alert.time}
                            </span>
                          </div>
                          <p className="font-semibold text-slate-200">
                            {alert.title}
                          </p>
                          <p className="opacity-80 text-[10px] mt-0.5">
                            {alert.text}
                          </p>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>

        {/* Section 3: Autonomous Remediation Timeline */}
        <div className="border border-slate-900 rounded-xl bg-slate-900/20 p-5 flex flex-col min-h-[420px] md:min-h-0 md:flex-1 md:overflow-hidden md:max-w-[350px] lg:max-w-[400px] xl:max-w-[450px] shrink-0">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2 mb-4 shrink-0">
            <ActivityIcon className="h-4 w-4 text-cyan-400" />
            Remediation Timeline
          </h2>

          {/* Timeline Stream Container */}
          <div className="flex-1 min-h-0 space-y-4 pr-1 overflow-y-auto scrollbar-thin">
            {timeline.map((event) => {
              let badgeColor = 'bg-slate-800 border-slate-700 text-slate-400';
              if (event.type === 'alert')
                badgeColor =
                  'bg-red-500/10 border-red-500/30 text-red-400 animate-pulse';
              if (event.type === 'analysis')
                badgeColor =
                  'bg-purple-500/10 border-purple-500/30 text-purple-400';
              if (event.type === 'decision')
                badgeColor =
                  'bg-indigo-500/10 border-indigo-500/30 text-indigo-400';
              if (event.type === 'remediation')
                badgeColor =
                  'bg-amber-500/10 border-amber-500/30 text-amber-400';
              if (event.type === 'resolution')
                badgeColor =
                  'bg-emerald-500/10 border-emerald-500/30 text-emerald-400';

              return (
                <div
                  key={event.id}
                  className="relative pl-5 border-l border-slate-900"
                >
                  {/* Node Dot */}
                  <div className="absolute -left-1.5 top-1.5 h-3 w-3 rounded-full bg-slate-950 border border-slate-800 flex items-center justify-center">
                    <span
                      className={`h-1.5 w-1.5 rounded-full ${
                        event.type === 'alert'
                          ? 'bg-red-500 animate-ping'
                          : event.type === 'resolution'
                            ? 'bg-emerald-400'
                            : 'bg-cyan-500'
                      }`}
                    />
                  </div>

                  {/* Metadata Header */}
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span
                      className={`text-[9px] font-mono font-bold uppercase px-1.5 py-0.5 rounded border ${badgeColor}`}
                    >
                      {event.type}
                    </span>
                    <span className="text-[10px] text-slate-600 font-mono">
                      {event.time}
                    </span>
                  </div>

                  {/* Event Content */}
                  <h4 className="text-xs font-semibold text-slate-200">
                    {event.title}
                  </h4>
                  <p className="text-[10px] text-slate-400 leading-normal mt-0.5">
                    {event.desc}
                  </p>
                </div>
              );
            })}
            <div ref={timelineEndRef} />
          </div>
        </div>
      </section>
      {/* Footer Branding Bar */}
      <footer className="border-t border-slate-950 py-3 px-6 flex items-center justify-between text-[10px] text-slate-600 font-mono shrink-0">
        <span>AUTHENTICATED VIA MODEL CONTEXT PROTOCOL (MCP)</span>
        <span>GOOGLE CLOUD RAPID AGENT SUITE &copy; 2026</span>
      </footer>
    </div>
  );
}
