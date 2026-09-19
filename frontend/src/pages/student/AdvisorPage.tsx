import { FormEvent, useState } from "react";

import {
  deleteChatHistory,
  getChatHistory,
  postAnalysis,
  postChat,
  type AnalysisOut,
} from "../../api/student";
import { useAuth } from "../../auth/AuthContext";
import { EmptyState } from "../../components/EmptyState";
import { ErrorMessage } from "../../components/ErrorMessage";
import { FallbackBanner } from "../../components/FallbackBanner";
import { Loading } from "../../components/Loading";
import { SimpleTable } from "../../components/SimpleTable";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Field } from "../../components/ui/Field";
import { Input } from "../../components/ui/Input";
import { PageHeader } from "../../components/ui/PageHeader";
import { useAsync } from "../../lib/useAsync";

export function AdvisorPage() {
  const { client } = useAuth();
  const [analysis, setAnalysis] = useState<AnalysisOut | null>(null);
  const [analysisError, setAnalysisError] = useState<unknown>(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [question, setQuestion] = useState("");
  const [chatError, setChatError] = useState<unknown>(null);
  const [chatLoading, setChatLoading] = useState(false);
  const [chatRefresh, setChatRefresh] = useState(0);
  const history = useAsync(() => getChatHistory(client), [client, chatRefresh]);

  async function loadAnalysis(refresh: boolean) {
    setAnalysisError(null);
    setAnalysisLoading(true);
    try {
      setAnalysis(await postAnalysis(client, refresh));
    } catch (err) {
      setAnalysis(null);
      setAnalysisError(err);
    } finally {
      setAnalysisLoading(false);
    }
  }

  async function onChat(event: FormEvent) {
    event.preventDefault();
    setChatError(null);
    setChatLoading(true);
    try {
      await postChat(client, question);
      setQuestion("");
      setChatRefresh((value) => value + 1);
    } catch (err) {
      setChatError(err);
    } finally {
      setChatLoading(false);
    }
  }

  async function onClearHistory() {
    setChatError(null);
    try {
      await deleteChatHistory(client);
      setChatRefresh((value) => value + 1);
    } catch (err) {
      setChatError(err);
    }
  }

  return (
    <section className="flex flex-col gap-6">
      <PageHeader title="AI Advisor" description="Facts stay separate from AI advice." />
      <Card>
        <h2 className="text-lg">Analysis</h2>
        <div className="mt-3">
          <Button onClick={() => void loadAnalysis(false)} disabled={analysisLoading}>
            {analysisLoading ? "Loading analysis…" : "Get analysis"}
          </Button>
        </div>
        {analysisLoading ? <div className="mt-3"><Loading label="Loading analysis…" /></div> : null}
        <div className="mt-3">
          <ErrorMessage error={analysisError} />
        </div>
        {!analysis && !analysisLoading && !analysisError ? (
          <div className="mt-3">
            <EmptyState title="No analysis yet" detail="Request an analysis to see facts and advice." />
          </div>
        ) : null}
        {analysis ? <AnalysisPanels analysis={analysis} /> : null}
      </Card>
      <Card>
        <h2 className="text-lg">Chat</h2>
        <div className="mt-3">
          {history.status === "loading" ? <Loading /> : null}
          {history.status === "error" ? <ErrorMessage error={history.error} /> : null}
          {history.status === "success" ? (
            history.data.messages.length === 0 ? (
              <EmptyState title="No chat messages" />
            ) : (
              <ul className="flex flex-col gap-3">
                {history.data.messages.map((message) => (
                  <li key={message.id} className="rounded-md border border-rule bg-ink-50 p-3 text-sm">
                    <strong>{message.role}</strong>
                    {message.source ? ` (${message.source})` : ""}: {message.content}
                    {message.source === "FALLBACK" ? <div className="mt-2"><FallbackBanner source={message.source} /></div> : null}
                  </li>
                ))}
              </ul>
            )
          ) : null}
        </div>
        <form onSubmit={(event) => void onChat(event)} className="mt-3 flex flex-col gap-2">
          <Field label="Question">
            <Input
              name="question"
              maxLength={500}
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              required
            />
          </Field>
          <ErrorMessage error={chatError} />
          <Button type="submit" disabled={chatLoading}>
            {chatLoading ? "Sending…" : "Send"}
          </Button>
        </form>
        <Button variant="ghost" className="mt-2" onClick={() => void onClearHistory()}>
          Clear history
        </Button>
      </Card>
    </section>
  );
}

function AnalysisPanels({ analysis }: { analysis: AnalysisOut }) {
  return (
    <div className="mt-3 flex flex-col gap-4 md:flex-row">
      <Card as="aside" className="flex-1" aria-labelledby="facts-heading">
        <h3 id="facts-heading" className="text-base">
          Facts
        </h3>
        <pre className="mt-2 overflow-x-auto whitespace-pre-wrap text-xs text-ink-700">
          {JSON.stringify(analysis.facts, null, 2)}
        </pre>
      </Card>
      <Card as="aside" className="flex-1" aria-labelledby="advice-heading">
        <h3 id="advice-heading" className="text-base">
          AI advice
        </h3>
        <div className="mt-2 flex flex-col gap-3">
          <FallbackBanner source={analysis.source} reason={analysis.fallback_reason} />
          <p>{analysis.advice.summary}</p>
          <p>Priority {analysis.advice.priority}</p>
          <h4>Concerns</h4>
          {analysis.advice.main_concerns.length === 0 ? (
            <EmptyState title="No concerns" />
          ) : (
            <SimpleTable
              caption="Main concerns"
              columns={["Factor", "Explanation"]}
              rows={analysis.advice.main_concerns.map((item) => [item.factor, item.explanation])}
            />
          )}
          <h4>Recommendations</h4>
          {analysis.advice.recommendations.length === 0 ? (
            <EmptyState title="No recommendations" />
          ) : (
            <SimpleTable
              caption="Recommendations"
              columns={["Action", "Reason", "Priority"]}
              rows={analysis.advice.recommendations.map((item) => [
                item.action,
                item.reason,
                item.priority,
              ])}
            />
          )}
        </div>
      </Card>
    </div>
  );
}
