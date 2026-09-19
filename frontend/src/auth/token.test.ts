import { ACCESS_TOKEN_KEY, clearAccessToken, createMemoryStore, getAccessToken, setAccessToken } from "./token";

describe("token store", () => {
  it("stores the access token on login and clears it on logout", () => {
    const store = createMemoryStore();
    expect(getAccessToken(store)).toBeNull();
    setAccessToken("jwt-token", store);
    expect(getAccessToken(store)).toBe("jwt-token");
    expect(store.getItem(ACCESS_TOKEN_KEY)).toBe("jwt-token");
    clearAccessToken(store);
    expect(getAccessToken(store)).toBeNull();
  });
});
