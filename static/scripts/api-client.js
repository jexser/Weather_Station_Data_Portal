function buildInlineErrorMessage(status, body, fallback404Message) {
    if (status === 400) {
        return body?.error?.message ?? "Invalid request.";
    }

    if (status === 404) {
        return fallback404Message ?? "No data found for the selected station / date.";
    }

    return body?.error?.message ?? "Failed to load data.";
}

async function fetchJsonOrThrow(url, options = {}) {
    const response = await fetch(url);

    if (response.ok) {
        return response.json();
    }

    const body = await response.json().catch(() => ({}));

    if (response.status >= 500) {
        window.location.assign(options.errorPagePath ?? "/error");
        throw new Error("Redirecting to error page.");
    }

    throw new Error(
        buildInlineErrorMessage(response.status, body, options.notFoundMessage)
    );
}

window.apiClient = {
    fetchJsonOrThrow,
};
