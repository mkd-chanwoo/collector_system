class QuotaController:
    """
    Domain token quota 관리 모듈
    """

    def __init__(self, target):
        # 목표 doamin
        self.target = target

        # domain별 token 수
        self.domain_tokens = {}

        # 전체 token 수
        self.total_tokens = 0

        # warning threshold
        self.warning_levels = [0.5, 0.75, 0.9, 0.95, 1.0]

        # domain별 이미 출력된 warning 기록
        self.warning_triggered = {domain: set() for domain in target}

        self.source_tokens = {}

    def to_dict(self):
        return {
            "domain_tokens": self.domain_tokens,
            "total_tokens": self.total_tokens,
            "source_tokens": self.source_tokens
        }
    
    def load_state(self, state):

        if not state:
            return

        self.domain_tokens = state.get("domain_tokens", {})
        self.total_tokens = state.get("total_tokens", 0)
        self.source_tokens = state.get("source_tokens", {})

        # warning_triggered 복구 (중요)
        for domain in self.domain_tokens:
            if domain not in self.warning_triggered:
                self.warning_triggered[domain] = set()

    def _check_warning(self, domain):
        """
        quota warning 체크
        """

        current = self.domain_tokens.get(domain, 0)
        target = self.target.get(domain)

        if target is None or target == 0:
            return

        ratio = current / target

        for level in self.warning_levels:

            if ratio >= level and level not in self.warning_triggered.get(domain, set()):

                percent = int(level * 100)

                print(
                    f"[WARNING] {domain} domain reached {percent}% of quota "
                    f"({current:,} / {target:,} tokens)"
                )

                self.warning_triggered[domain].add(level)

    def update(self, domain, tokens, source):
        """
        domain token 수 업데이트
        """
        if domain not in self.domain_tokens:
            self.domain_tokens[domain] = 0
        if domain not in self.warning_triggered:
            self.warning_triggered[domain] = set()

        if domain not in self.source_tokens:
            self.source_tokens[domain] = {}

        if source not in self.source_tokens[domain]:
            self.source_tokens[domain][source] = 0

        self.source_tokens[domain][source] += tokens

        self.domain_tokens[domain] += tokens

        self.total_tokens += tokens

        self._check_warning(domain)

    def get_domain_tokens(self, domain):
        """
        특정 domain token 조회
        """

        return self.domain_tokens.get(domain, 0)

    def get_total_tokens(self):
        """
        전체 token 수 조회
        """

        return self.total_tokens

    def summary(self):
        """
        현재 token 통계 출력
        """

        print("\n===== TOKEN SUMMARY =====")

        for domain, tokens in self.domain_tokens.items():
            target = self.target.get(domain, 0)
            print(f"{domain} : {tokens:,} / {target:,}")

        print("\n===== SOURCE CONTRIBUTION =====")

        for domain, sources in self.source_tokens.items():

            print(f"\n[{domain}]")

            for source, tokens in sources.items():

                print(f"{source} : {tokens:,}")

        print(f"\nTOTAL TOKENS : {self.total_tokens:,}")

        print("=========================\n")