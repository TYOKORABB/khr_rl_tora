// udp-drain-only.patch の単体テスト（ホストの g++）。khr_udp_drain.h だけを使う。2026-11-20
//   g++ -std=c++17 -Wall -Wextra -Werror -I _work/drainonly/Meridian_LITE_for_ESP32/src test/test_udp_drain.cpp -o _work/test_udp_drain && _work/test_udp_drain
#include <cstdio>
#include <vector>
#include "khr_udp_drain.h"

static int fails = 0;
#define CHECK(c, ...) do { if (!(c)) { std::printf("  NG: " __VA_ARGS__); std::printf("\n"); fails++; } } while (0)
static uint16_t seq_next(uint16_t s) { return (uint16_t)((s + 1) % 60000); } // 梶田版の mrd_seq_predict_num と同じ（0〜59999 で一巡）

struct Pkt { int16_t master, seq; bool broken; };
static void make(const Pkt &p, int16_t *m) {
  for (int i = 0; i < KHR_MRDM_LEN; i++) m[i] = 0;
  m[0] = p.master; m[1] = p.seq; m[2] = (int16_t)(p.seq * 7);
  int sum = 0;
  for (int i = 0; i < KHR_MRDM_LEN - 1; i++) sum += m[i];
  m[KHR_MRDM_LEN - 1] = (int16_t)(~sum);
  if (p.broken) m[3] = 1;
}
static int run(Pkt cur_p, std::vector<Pkt> rest, int16_t *cur, uint16_t &prev, size_t &left, int max = KHR_DRAIN_MAX) {
  make(cur_p, cur);
  size_t pos = 0;
  auto recv = [&](int16_t *dst) { if (pos >= rest.size()) return false; make(rest[pos++], dst); return true; };
  const int n = khr_udp_drain(cur, recv, prev, max);
  left = rest.size() - pos;
  return n;
}

int main() {
  const int16_t N = KHR_MRDM_LEN, SPECIAL = 10003;
  int16_t cur[KHR_MRDM_LEN]; uint16_t prev; size_t left; int n;
  std::printf("[1] 溜まった通常パケットは読み捨て、最新だけ残す\n");
  prev = 0xFFFF;
  n = run({N, 1, false}, {{N, 2, false}, {N, 3, false}, {N, 4, false}, {N, 5, false}}, cur, prev, left);
  CHECK(n == 4 && cur[1] == 5 && cur[2] == 35 && prev == 4 && left == 0, "n=%d seq=%d prev=%u", n, cur[1], prev);
  CHECK(khr_cksm_ok(cur), "残したパケットのチェックサム");
  CHECK(seq_next(prev) == (uint16_t)cur[1], "1 つ前の番号 +1 が残した番号（スキップと数えない）");
  std::printf("[2] 特殊コマンドは読み捨てない（来たらそれを残して止める）\n");
  prev = 0;
  n = run({N, 1, false}, {{N, 2, false}, {SPECIAL, 3, false}, {N, 4, false}}, cur, prev, left);
  CHECK(n == 2 && cur[0] == SPECIAL && cur[1] == 3 && prev == 2 && left == 1, "n=%d master=%d left=%zu", n, cur[0], left);
  prev = 77;
  n = run({SPECIAL, 1, false}, {{N, 2, false}}, cur, prev, left);
  CHECK(n == 0 && cur[0] == SPECIAL && prev == 77 && left == 1, "いま持っているのが特殊コマンド n=%d", n);
  n = run({0, 1, false}, {{N, 2, false}}, cur, prev, left);
  CHECK(n == 0 && cur[0] == 0 && left == 1, "全サーボ脱力（マスターコマンド 0）を読み捨てた n=%d", n);
  std::printf("[3] チェックサムの合わないパケットは捨てる・空なら変えない・上限で止める\n");
  prev = 0;
  n = run({N, 1, false}, {{N, 2, true}, {N, 3, false}}, cur, prev, left);
  CHECK(n == 1 && cur[1] == 3 && prev == 1 && left == 0, "n=%d seq=%d prev=%u", n, cur[1], prev);
  CHECK(seq_next(prev) != (uint16_t)cur[1], "壊れたパケットの分はスキップとして残る");
  prev = 55;
  n = run({N, 9, false}, {}, cur, prev, left);
  CHECK(n == 0 && cur[1] == 9 && prev == 55, "空の受信バッファで変わった n=%d", n);
  std::vector<Pkt> many;
  for (int16_t s = 2; s < 40; s++) many.push_back({N, s, false});
  n = run({N, 1, false}, many, cur, prev, left);
  CHECK(n == KHR_DRAIN_MAX && left == many.size() - KHR_DRAIN_MAX, "上限 n=%d left=%zu", n, left);
  std::printf(fails ? "NG %d\n" : "OK（全部通った）\n", fails);
  return fails ? 1 : 0;
}
