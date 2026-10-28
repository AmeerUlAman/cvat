// Copyright (C) CVAT.ai Corporation
//
// SPDX-License-Identifier: MIT

import './styles.scss';

import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useParams } from 'react-router';
import {
    BarElement, CategoryScale, Chart as ChartJS, ChartData, ChartOptions, LinearScale, Tooltip,
} from 'chart.js';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import { Bar } from 'react-chartjs-2';
import Alert from 'antd/lib/alert';
import Button from 'antd/lib/button';
import Empty from 'antd/lib/empty';
import { Col, Row } from 'antd/lib/grid';
import Select from 'antd/lib/select';
import Title from 'antd/lib/typography/Title';
import Text from 'antd/lib/typography/Text';

import CVATLoadingSpinner from 'components/common/loading-spinner';
import GoBackButton from 'components/common/go-back-button';

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, ChartDataLabels);

interface LabelCount {
    label_id: number;
    label: string;
    count: number;
}

interface CountsResponse {
    task_id: number;
    source: AnnotationSource;
    counts: LabelCount[];
}

type AnnotationSource = '' | 'manual' | 'auto' | 'semi-auto' | 'file' | 'consensus';

const SOURCE_OPTIONS: { value: AnnotationSource; label: string }[] = [
    { value: '', label: 'All sources' },
    { value: 'manual', label: 'Manual' },
    { value: 'auto', label: 'Automatic' },
    { value: 'semi-auto', label: 'Semi-automatic' },
    { value: 'file', label: 'Imported from file' },
    { value: 'consensus', label: 'Consensus' },
];

function TaskAnnotationCountsPage(): JSX.Element {
    const taskId = Number(useParams<{ id: string }>().id);
    const [counts, setCounts] = useState<LabelCount[]>([]);
    const [fetching, setFetching] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [retryCount, setRetryCount] = useState(0);
    const [source, setSource] = useState<AnnotationSource>('');

    const chartData = useMemo<ChartData<'bar'>>(() => ({
        labels: counts.map(({ label }) => label),
        datasets: [{
            label: 'Annotations',
            data: counts.map(({ count }) => count),
            backgroundColor: 'rgba(24, 144, 255, 0.75)',
            borderColor: '#1890ff',
            borderWidth: 1,
            borderRadius: 4,
            minBarLength: 3,
        }],
    }), [counts]);

    const chartOptions = useMemo<ChartOptions<'bar'>>(() => ({
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        layout: {
            padding: { right: 48 },
        },
        plugins: {
            legend: { display: false },
            tooltip: {
                callbacks: {
                    label: (context) => `${context.parsed.x.toLocaleString()} annotations`,
                },
            },
            datalabels: {
                anchor: 'end',
                align: 'end',
                color: '#303030',
                formatter: (value: number) => value.toLocaleString(),
                font: { weight: 'bold' },
            },
        },
        scales: {
            x: {
                beginAtZero: true,
                grace: '10%',
                title: {
                    display: true,
                    text: 'Annotation count',
                },
                ticks: { precision: 0 },
            },
            y: {
                grid: { display: false },
                title: {
                    display: true,
                    text: 'Class',
                },
                ticks: { autoSkip: false },
            },
        },
    }), []);

    const fetchCounts = useCallback((signal?: AbortSignal): Promise<void> => {
        setFetching(true);
        setError(null);

        const sourceQuery = source ? `?source=${encodeURIComponent(source)}` : '';
        return fetch(`/api/tasks/${taskId}/annotation-counts${sourceQuery}`, {
            method: 'GET',
            credentials: 'same-origin',
            headers: { Accept: 'application/vnd.cvat+json' },
            signal,
        }).then(async (response) => {
            if (!response.ok) {
                throw new Error(`The request failed (${response.status})`);
            }
            return response.json() as Promise<CountsResponse>;
        }).then((result) => {
            if (!Array.isArray(result.counts)) {
                throw new Error('The server returned an invalid annotation count response');
            }
            setCounts(result.counts);
        }).catch((requestError: unknown) => {
            if (!signal?.aborted) {
                setError(requestError instanceof Error ? requestError.message : 'Could not load annotation counts');
            }
        }).finally(() => {
            if (!signal?.aborted) {
                setFetching(false);
            }
        });
    }, [taskId, source]);

    useEffect(() => {
        const controller = new AbortController();
        void fetchCounts(controller.signal);
        return () => controller.abort();
    }, [fetchCounts, retryCount]);

    const websocketRef = useRef<WebSocket | null>(null);
    useEffect(() => {
        if (typeof window === 'undefined' || !('WebSocket' in window)) {
            return undefined;
        }

        let isActive = true;
        let retryTimeoutId: number | undefined;
        let reconnectDelay = 1000;

        const createWebSocket = (): void => {
            if (!isActive) {
                return;
            }

            if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
                return;
            }

            const socketUrl = new URL(`/ws/tasks/${taskId}/annotation-counts`, window.location.origin);
            socketUrl.protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const socket = new WebSocket(socketUrl.toString());
            websocketRef.current = socket;

            socket.onopen = () => {
                reconnectDelay = 1000;
                setError(null);
            };

            socket.onmessage = (event) => {
                const rawMessage = typeof event.data === 'string' ? event.data : '';
                if (!rawMessage) {
                    return;
                }

                try {
                    const payload = JSON.parse(rawMessage) as { type?: string; task_id?: number };
                    if (payload.type === 'ping') {
                        return;
                    }
                    if (payload.type === 'annotation_counts_updated' && payload.task_id === taskId) {
                        const controller = new AbortController();
                        void fetchCounts(controller.signal);
                        setTimeout(() => controller.abort(), 5000);
                    }
                } catch {
                    // Ignore malformed push notifications and fall back to the next explicit refresh.
                }
            };

            socket.onerror = () => {
                // Reconnect with backoff after a transient socket failure.
            };

            socket.onclose = () => {
                if (!isActive) {
                    return;
                }

                retryTimeoutId = window.setTimeout(() => {
                    reconnectDelay = Math.min(reconnectDelay * 2, 15000);
                    createWebSocket();
                }, reconnectDelay);
            };
        };

        createWebSocket();

        return () => {
            isActive = false;
            if (retryTimeoutId) {
                window.clearTimeout(retryTimeoutId);
            }
            websocketRef.current?.close();
        };
    }, [fetchCounts, taskId]);

    return (
        <div className='cvat-annotation-counts-page'>
            <div className='cvat-annotation-counts-wrapper'>
                <Row justify='center'>
                    <Col span={22} xl={18} xxl={14} className='cvat-task-top-bar'>
                        <GoBackButton />
                    </Col>
                </Row>
                <Row justify='center' className='cvat-annotation-counts-inner-wrapper'>
                    <Col span={22} xl={18} xxl={14} className='cvat-annotation-counts-inner'>
                        <header className='cvat-annotation-counts-header'>
                            <div>
                                <Title level={2}>Annotation counts</Title>
                                <Text type='secondary'>Task {taskId} · saved shapes grouped by label</Text>
                            </div>
                            <label className='cvat-annotation-counts-source-filter'>
                                <Text>Annotation source</Text>
                                <Select<AnnotationSource>
                                    value={source}
                                    onChange={setSource}
                                    options={SOURCE_OPTIONS}
                                    aria-label='Filter annotation counts by source'
                                />
                            </label>
                        </header>
                        <section aria-live='polite' className='cvat-annotation-counts-content'>
                            { fetching && <CVATLoadingSpinner /> }
                            { !fetching && error && (
                                <Alert
                                    type='error'
                                    showIcon
                                    message='Could not load annotation counts'
                                    description={error}
                                    action={(
                                        <Button size='small' onClick={() => setRetryCount((previous) => previous + 1)}>
                                            Try again
                                        </Button>
                                    )}
                                />
                            ) }
                            { !fetching && !error && counts.length === 0 && (
                                <Empty
                                    description={source ?
                                        'No saved shapes match this source.' :
                                        'No saved shapes were found for this task.'}
                                />
                            ) }
                            { !fetching && !error && counts.length > 0 && (
                                <div
                                    className='cvat-annotation-counts-chart'
                                    style={{ height: Math.max(480, counts.length * 32) }}
                                >
                                    <Bar
                                        data={chartData}
                                        options={chartOptions}
                                        aria-label='Horizontal bar chart of saved shapes grouped by class'
                                    />
                                </div>
                            ) }
                        </section>
                    </Col>
                </Row>
            </div>
        </div>
    );
}

export default React.memo(TaskAnnotationCountsPage);
