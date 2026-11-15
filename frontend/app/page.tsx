"use client";

import { useCallback, useEffect, useState } from "react";
import { getDashboardOverview } from "@/lib/api";

interface DashboardData {
	tasks: {
		total: number;
		by_status: {
			pending: number;
			assigned: number;
			in_progress: number;
			completed: number;
		};
	};
	assignments: {
		total: number;
		by_status: {
			assigned: number;
			accepted: number;
			rejected: number;
			no_response: number;
		};
		acceptance_rate: number;
		timeout_rate: number;
	};
	contributors: {
		total: number;
		available: number;
		unavailable: number;
		workload: {
			contributor_id: number;
			name: string;
			skills: string[];
			available: boolean;
			max_capacity: number;
			active_assignments: number;
			remaining_capacity: number;
			utilization_percentage: number;
		}[];
	};
	recent_activities: {
		id: number;
		entity_type: string;
		entity_id: number;
		action: string;
		details: string | null;
		created_at: string;
	}[];
}

export default function Home() {
	const [data, setData] = useState<DashboardData | null>(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");

	const loadDashboard = useCallback(async () => {
		try {
			setLoading(true);
			setError("");

			const result = await getDashboardOverview();
			setData(result);
		} catch {
			setError("Unable to load dashboard. Check your backend connection.");
		} finally {
			setLoading(false);
		}
	}, []);

	useEffect(() => {
		loadDashboard();
	}, [loadDashboard]);

	const cards = [
		{
			title: "Total Tasks",
			value: data?.tasks.total ?? 0,
			subtitle: `${data?.tasks.by_status.pending ?? 0} pending`,
			color: "border-blue-500",
		},
		{
			title: "Contributors",
			value: data?.contributors.total ?? 0,
			subtitle: `${data?.contributors.available ?? 0} available`,
			color: "border-emerald-500",
		},
		{
			title: "Acceptance Rate",
			value: `${data?.assignments.acceptance_rate ?? 0}%`,
			subtitle: `${data?.assignments.by_status.accepted ?? 0} accepted`,
			color: "border-violet-500",
		},
		{
			title: "Timeout Rate",
			value: `${data?.assignments.timeout_rate ?? 0}%`,
			subtitle: `${data?.assignments.by_status.no_response ?? 0} timeouts`,
			color: "border-amber-500",
		},
	];

	const taskStatuses = [
		["Pending", data?.tasks.by_status.pending ?? 0, "bg-amber-500"],
		["Assigned", data?.tasks.by_status.assigned ?? 0, "bg-blue-500"],
		["In Progress", data?.tasks.by_status.in_progress ?? 0, "bg-violet-500"],
		["Completed", data?.tasks.by_status.completed ?? 0, "bg-emerald-500"],
	] as const;

	return (
		<main className="min-h-screen bg-slate-950 px-5 py-8 text-slate-100 sm:px-8">
			<div className="mx-auto max-w-7xl">

				<header className="mb-8 flex flex-wrap items-center justify-between gap-4">
					<div>
						<p className="text-sm font-semibold tracking-widest text-blue-400">
							TASK ROUTING SYSTEM
						</p>
						<h1 className="mt-2 text-3xl font-bold">Dashboard</h1>
						<p className="mt-2 text-sm text-slate-400">
							Monitor tasks, assignments and contributor performance.
						</p>
					</div>

					<div className="flex items-center gap-3">
						<span className="rounded-full border border-slate-700 px-3 py-2 text-xs">
							<span className="mr-2 text-emerald-400">●</span>
							{data ? "Backend Connected" : "Checking Backend"}
						</span>

						<button
							onClick={loadDashboard}
							disabled={loading}
							className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold hover:bg-blue-500 disabled:opacity-50"
						>
							{loading ? "Loading..." : "Refresh"}
						</button>
					</div>
				</header>

				{error && (
					<div className="mb-6 rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-red-300">
						{error}
					</div>
				)}

				{loading && !data && (
					<p className="py-12 text-center text-slate-400">
						Loading dashboard data...
					</p>
				)}

				{data && (
					<>
						<section className="mb-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
							{cards.map((card) => (
								<div
									key={card.title}
									className={`rounded-xl border border-slate-800 border-l-4 ${card.color} bg-slate-900 p-5`}
								>
									<p className="text-sm text-slate-400">{card.title}</p>
									<h2 className="mt-3 text-3xl font-bold">{card.value}</h2>
									<p className="mt-2 text-xs text-slate-500">
										{card.subtitle}
									</p>
								</div>
							))}
						</section>

						<section className="mb-8 grid gap-6 lg:grid-cols-2">

							<div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
								<h2 className="mb-6 text-lg font-semibold">
									Task Distribution
								</h2>

								<div className="space-y-6">
									{taskStatuses.map(([label, count, color]) => {
										const percentage = data.tasks.total
											? (count / data.tasks.total) * 100
											: 0;

										return (
											<div key={label}>
												<div className="mb-2 flex justify-between text-sm">
													<span className="text-slate-300">{label}</span>
													<span className="font-semibold">{count}</span>
												</div>

												<div className="h-2 overflow-hidden rounded-full bg-slate-800">
													<div
														className={`h-full rounded-full ${color}`}
														style={{ width: `${percentage}%` }}
													/>
												</div>
											</div>
										);
									})}
								</div>
							</div>

							<div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
								<h2 className="mb-6 text-lg font-semibold">
									Assignment Overview
								</h2>

								<div className="grid grid-cols-2 gap-4">
									{Object.entries(data.assignments.by_status).map(
										([status, count]) => (
											<div key={status} className="rounded-lg bg-slate-800 p-4">
												<p className="text-xs capitalize text-slate-400">
													{status.replaceAll("_", " ")}
												</p>
												<p className="mt-2 text-2xl font-bold">{count}</p>
											</div>
										)
									)}

									<div className="rounded-lg bg-slate-800 p-4">
										<p className="text-xs text-slate-400">Total</p>
										<p className="mt-2 text-2xl font-bold">
											{data.assignments.total}
										</p>
									</div>
								</div>
							</div>
						</section>

						<section className="mb-8 rounded-xl border border-slate-800 bg-slate-900 p-6">
							<h2 className="mb-6 text-lg font-semibold">
								Contributor Workload
							</h2>

							<div className="overflow-x-auto">
								<table className="w-full min-w-[600px] text-left text-sm">
									<thead>
										<tr className="border-b border-slate-800 text-slate-400">
											<th className="pb-4">Contributor</th>
											<th className="pb-4">Skills</th>
											<th className="pb-4">Availability</th>
											<th className="pb-4">Workload</th>
											<th className="pb-4">Utilization</th>
										</tr>
									</thead>

									<tbody>
										{data.contributors.workload.map((person) => (
											<tr
												key={person.contributor_id}
												className="border-b border-slate-800/70"
											>
												<td className="py-4 font-medium">{person.name}</td>
												<td className="py-4 text-slate-400">
													{person.skills.join(", ") || "No skills"}
												</td>
												<td className="py-4">
													{person.available ? "Available" : "Unavailable"}
												</td>
												<td className="py-4">
													{person.active_assignments} / {person.max_capacity}
												</td>
												<td className="py-4">
													<div className="flex items-center gap-2">
														<div className="h-2 w-20 rounded-full bg-slate-800">
															<div
																className="h-2 rounded-full bg-blue-500"
																style={{
																	width: `${Math.min(person.utilization_percentage, 100)}%`,
																}}
															/>
														</div>
														{person.utilization_percentage}%
													</div>
												</td>
											</tr>
										))}
									</tbody>
								</table>
							</div>
						</section>

						<section className="rounded-xl border border-slate-800 bg-slate-900 p-6">
							<h2 className="mb-6 text-lg font-semibold">Recent Activity</h2>

							{data.recent_activities.length === 0 ? (
								<p className="text-sm text-slate-400">No recent activity.</p>
							) : (
								<div className="space-y-5">
									{data.recent_activities.map((activity) => (
										<div
											key={activity.id}
											className="flex flex-wrap justify-between gap-3 border-b border-slate-800 pb-4"
										>
											<div>
												<p className="font-medium capitalize">
													{activity.action.replaceAll("_", " ")}
												</p>
												<p className="mt-1 text-sm text-slate-400">
													{activity.details}
												</p>
											</div>

											<span className="text-xs text-slate-500">
												{new Date(activity.created_at).toLocaleString()}
											</span>
										</div>
									))}
								</div>
							)}
						</section>
					</>
				)}
			</div>
		</main>
	);
}