// We'll only update the pull request if it's more than 50 commits behind.
const MAX_COMMITS_BEHIND = 5;

function ready() {
  const base = $event.pullRequest.base.ref;
  const head = $event.pullRequest.head.ref;
  const { behindBy } = $github.compareCommits({ base, head });
  if (behindBy > MAX_COMMITS_BEHIND) {
    $github.addComment(
      `Pull request is ${behindBy} commits behind ${base}. ` +
      `Synchronizing pull request with latest commits before queuing.`
    );

    // Update the pull request with the latest commit from its base branch using
    // the repository's configured strategy (rebase or merge).
    $mergequeue.synchronizePullRequest();
  } else {
    $github.addComment(
      `Pull request is ${behindBy} comits behind ${base}. ` +
      `Not synchronizisng pull request with the latest commits.`
    );
  }
}
