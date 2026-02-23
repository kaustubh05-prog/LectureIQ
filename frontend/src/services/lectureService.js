import api from "./api";

export const lectureService = {
    upload: (formData, onProgress) =>
        api.post("/api/lectures/upload", formData, {
            headers: { "Content-Type": "multipart/form-data" },
            onUploadProgress: (e) => {
                if (onProgress && e.total) {
                    onProgress(Math.round((e.loaded / e.total) * 100));
                }
            },
        }),

    list: (page = 1) =>
        api.get("/api/lectures", { params: { page, limit: 20 } }),

    getDetail: (id) =>
        api.get(`/api/lectures/${id}`),

    getStatus: (id) =>
        api.get(`/api/lectures/${id}/status`),

    delete: (id) =>
        api.delete(`/api/lectures/${id}`),

    submitQuiz: (id, answers) =>
        api.post(`/api/lectures/${id}/quiz/submit`, { answers }),
};
