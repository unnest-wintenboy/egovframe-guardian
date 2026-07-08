<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
<section class="notice-list">
    <h1>공지사항</h1>
    <form method="get" action="${pageContext.request.contextPath}/notice">
        <input type="search" name="keyword" value="${param.keyword}" />
        <button type="submit">검색</button>
    </form>
    <table>
        <thead>
        <tr>
            <th>번호</th>
            <th>제목</th>
            <th>등록일</th>
        </tr>
        </thead>
        <tbody>
        <c:forEach var="notice" items="${notices}">
            <tr>
                <td>${notice.noticeId}</td>
                <td>${notice.title}</td>
                <td>${notice.createdAt}</td>
            </tr>
        </c:forEach>
        </tbody>
    </table>
</section>
