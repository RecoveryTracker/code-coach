import { Component, type ErrorInfo, type ReactNode } from "react";

type Props = { children: ReactNode };
type State = { error: Error | null };

/**
 * Catches render/runtime errors in the tree below it so one bad render shows a
 * recoverable message instead of a blank white screen. Your typed code lives in
 * localStorage, so a reload does not lose your work.
 */
export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    // Surface it for debugging; not shown to the student.
    console.error("Code Coach crashed:", error, info.componentStack);
  }

  render() {
    if (this.state.error) {
      return (
        <div className="ws-boot">
          <h1>Code Coach hit a snag</h1>
          <p>Something in the app broke. Your typed work is saved.</p>
          <p className="muted">{this.state.error.message}</p>
          <button
            type="button"
            className="ws-btn primary"
            onClick={() => window.location.reload()}
          >
            Reload
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
